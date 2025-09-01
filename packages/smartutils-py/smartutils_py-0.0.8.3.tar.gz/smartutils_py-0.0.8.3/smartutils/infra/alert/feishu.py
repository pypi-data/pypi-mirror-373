import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from smartutils.config.const import ConfKey
from smartutils.config.schema.alert_feishu import AlertFeishuConf
from smartutils.config.schema.client import ApiConf, ClientConf, ClientType
from smartutils.ctx.const import CTXKey
from smartutils.ctx.manager import CTXVarManager
from smartutils.design import singleton
from smartutils.infra.client.http import HttpClient
from smartutils.infra.resource.abstract import AbstractAsyncResource
from smartutils.infra.resource.manager.manager import CTXResourceManager
from smartutils.init.factory import InitByConfFactory
from smartutils.init.mixin import LibraryCheckMixin
from smartutils.log import logger
from smartutils.time import get_now_str


class AlertFeishu(AbstractAsyncResource):
    def __init__(self, conf: AlertFeishuConf):
        self._conf = conf
        self._clients = []
        if not conf.enable:
            return

        for webhook_url in conf.webhooks:
            http_conf = ClientConf(
                type=ClientType.HTTP,
                endpoint=webhook_url,
                timeout=5,
                verify_tls=True,
                apis={"send_alert": ApiConf(path="", method="POST", timeout=5)},
            )
            self._clients.append(
                HttpClient(http_conf, name=f"alert_feishu_{webhook_url}")
            )

    async def alert(self, title: str, content: str):
        if not self._conf.enable or not self._clients:
            logger.info("AlertFeishu is disabled or no clients")
            return []

        now = get_now_str()
        payload = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": f"🚨告警: {title}",
                        "content": [
                            [
                                {"tag": "text", "text": "内容："},
                                {"tag": "text", "text": content},
                            ],
                            [
                                {"tag": "text", "text": "时间："},
                                {"tag": "text", "text": now},
                            ],
                        ],
                    }
                }
            },
        }

        async def send_one(client):
            try:
                resp = await client.send_alert(json=payload)
                return resp.status_code == 200
            except Exception:
                return False

        return await asyncio.gather(
            *[send_one(client) for client in self._clients], return_exceptions=False
        )

    async def close(self):
        for client in self._clients:
            await client.close()

    async def ping(self) -> bool:
        return True

    @asynccontextmanager
    async def db(self, use_transaction: bool):
        yield self


@singleton
@CTXVarManager.register(CTXKey.ALERT_FEISHU)
class AlertFeishuManager(LibraryCheckMixin, CTXResourceManager[AlertFeishu]):
    def __init__(self, conf: Optional[AlertFeishuConf] = None):
        self.check(conf=conf)

        resources = {ConfKey.GROUP_DEFAULT.value: AlertFeishu(conf)}
        super().__init__(resources=resources, ctx_key=CTXKey.ALERT_FEISHU)

    @property
    def curr(self) -> AlertFeishu:
        return super().curr


@InitByConfFactory.register(ConfKey.ALERT_FEISHU)
def _(conf):
    AlertFeishuManager(conf)
