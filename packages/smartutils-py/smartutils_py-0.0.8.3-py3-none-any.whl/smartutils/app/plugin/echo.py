from typing import Awaitable, Callable

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import HeaderKey, MiddlewarePluginOrder
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.config.schema.middleware import MiddlewarePluginKey
from smartutils.design import SingletonMeta
from smartutils.error.base import BaseDataDict

__all__ = ["EchoPlugin"]


@MiddlewarePluginFactory.register(
    MiddlewarePluginKey.ECHO, order=MiddlewarePluginOrder.ECHO
)
class EchoPlugin(AbstractMiddlewarePlugin, metaclass=SingletonMeta):
    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],  # 未调用
    ) -> ResponseAdapter:
        echo_data = BaseDataDict(
            {
                "code": 0,
                "msg": "ok echo",
                "headers": dict(req.headers),
                "query_params": dict(req.query_params),
                "client_host": req.client_host,
                "method": req.method,
                "url": req.url,
                "path": req.path,
                "cookies": req.get_cookie(HeaderKey.X_ECHO),
            }
        )
        return self._resp_fn(echo_data)
