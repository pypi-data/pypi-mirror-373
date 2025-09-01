from typing import Awaitable, Callable

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import HeaderKey, MiddlewarePluginOrder
from smartutils.app.plugin.common import CustomHeader
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.config.schema.middleware import MiddlewarePluginKey
from smartutils.ctx import CTXKey, CTXVarManager
from smartutils.design import SingletonMeta

__all__ = ["HeaderPlugin"]


@MiddlewarePluginFactory.register(
    MiddlewarePluginKey.HEADER, order=MiddlewarePluginOrder.HEADER
)
class HeaderPlugin(AbstractMiddlewarePlugin, metaclass=SingletonMeta):
    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        trace_id = CustomHeader.traceid(req)
        if not trace_id:
            trace_id = req.gen_trace_id()
        userid = CustomHeader.userid(req)
        username = CustomHeader.username(req)
        permission_user_ids = CustomHeader.permission_user_ids(req)
        with (
            CTXVarManager.use(CTXKey.TRACE_ID, trace_id),
            CTXVarManager.use(CTXKey.USERID, userid),
            CTXVarManager.use(CTXKey.USERNAME, username),
            CTXVarManager.use(CTXKey.PERMISSION_USER_IDS, permission_user_ids),
        ):
            resp: ResponseAdapter = await next_adapter()
            resp.set_header(HeaderKey.X_TRACE_ID, trace_id)
            return resp
