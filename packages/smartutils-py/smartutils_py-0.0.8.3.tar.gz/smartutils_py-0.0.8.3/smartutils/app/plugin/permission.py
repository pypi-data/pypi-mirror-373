from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, Dict, Optional, Tuple

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import MiddlewarePluginOrder
from smartutils.app.plugin.abstract import AuthBase
from smartutils.app.plugin.common import CustomHeader
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.config.schema.middleware import (
    MiddlewarePluginKey,
    MiddlewarePluginSetting,
)
from smartutils.design import SingletonMeta
from smartutils.error.sys import UnauthorizedError

try:
    from httpx import Response
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    from httpx import Response


@MiddlewarePluginFactory.register(
    MiddlewarePluginKey.PERMISSION, order=MiddlewarePluginOrder.PERMISSION
)
class PermissionPlugin(AuthBase, AbstractMiddlewarePlugin, metaclass=SingletonMeta):
    def __init__(self, *, conf: MiddlewarePluginSetting):
        super().__init__(conf=conf, plugin_conf=conf.permission)

    # async def _local(self, req: RequestAdapter) -> Tuple[Optional[Dict], str]:
    #     # TODO: 完善local调用
    #     access_token, msg = self.access_token(req)
    #     if msg:
    #         return None, msg
    #     return {}, ""

    async def _remote(self, req: RequestAdapter) -> Tuple[Optional[Dict], str]:
        cookies, msg = self.mk_cookies(req)
        if msg:
            return None, msg

        resp: Response = await self._client.permission(
            cookies=cookies, params={"api": req.path}
        )
        data, msg = self._client.check_resp(resp)
        if msg:
            return None, msg

        if not data:
            return None, "no data."

        return data, ""

    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        if self._plugin_conf.local:
            # data, msg = await self._local(req)
            data = {}
            msg = "no supported local now."
        else:
            data, msg = await self._remote(req)

        if msg or not data:
            return self._resp_fn(UnauthorizedError(f"{self.name} {msg}").as_dict)

        can_access = data.get("can_access", False)
        if not can_access:
            return self._resp_fn(
                UnauthorizedError(f"{self.name} no permission").as_dict
            )

        CustomHeader.permission_user_ids(req, data.get("user_ids"), set_value=True)

        resp: ResponseAdapter = await next_adapter()
        return resp
