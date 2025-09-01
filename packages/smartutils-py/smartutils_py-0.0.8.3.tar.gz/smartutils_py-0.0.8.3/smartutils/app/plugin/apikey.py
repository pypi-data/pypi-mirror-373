import hashlib
from typing import Awaitable, Callable

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import MiddlewarePluginOrder
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.config.schema.middleware import MiddlewarePluginKey
from smartutils.design import SingletonMeta
from smartutils.error.sys import UnauthorizedError

__all__ = ["ApiKeyPlugin"]


def calc_signature(key: str, timestamp: str, secret: str):
    """
    计算签名字符串。
    :param key: API Key
    :param timestamp: 时间戳
    :param secret: API 密钥
    :return: sha256 签名结果
    """
    plain = f"key={key}&timestamp={timestamp}&secret={secret}"
    return hashlib.sha256(plain.encode()).hexdigest()


@MiddlewarePluginFactory.register(
    MiddlewarePluginKey.APIKEY, order=MiddlewarePluginOrder.APIKEY
)
class ApiKeyPlugin(AbstractMiddlewarePlugin, metaclass=SingletonMeta):
    """
    API Key 鉴权中间件插件，实现请求头 apikey 及签名校验。
    """

    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        """
        核心处理流程：
        1. 校验 apikey 是否有效
        2. 如果配置开启 secret 校验，则校验 timestamp 与 signature
        3. 校验不通过时返回 401 未授权响应，通过则传递到下游
        :param req: 请求适配器
        :param next_adapter: 下一个适配器，标准中间件模式
        """
        # 从请求头获取 apikey
        api_key = req.get_header(self._conf.apikey.header_key)  # type: ignore
        # 校验 apikey 是否在允许列表
        if api_key not in self._conf.apikey.keys:
            return self._resp_fn(
                UnauthorizedError(
                    f"ApiKeyPlugin invalid key, received: {api_key}"
                ).as_dict
            )

        # 如果需要校验签名
        if self._conf.apikey.secret:
            signature = req.get_header(self._conf.apikey.header_signature)  # type: ignore
            timestamp = req.get_header(self._conf.apikey.header_timestamp)  # type: ignore
            if not signature or not timestamp:
                return self._resp_fn(
                    UnauthorizedError(
                        "ApiKeyPlugin missing signature or timestamp"
                    ).as_dict
                )
            # 按固定算法计算本地签名
            expected_sign = calc_signature(api_key, timestamp, self._conf.apikey.secret)
            if signature != expected_sign:
                return self._resp_fn(
                    UnauthorizedError("ApiKeyPlugin invalid signature").as_dict
                )

        # 全部校验通过，调用后续中间件
        resp: ResponseAdapter = await next_adapter()
        return resp
