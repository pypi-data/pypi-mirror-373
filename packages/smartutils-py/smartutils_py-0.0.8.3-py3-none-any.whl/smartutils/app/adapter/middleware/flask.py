from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

try:
    import flask
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    import flask


from smartutils.app.adapter.middleware.abstract import (
    AbstractMiddleware,
    AbstractMiddlewarePlugin,
)
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey
from smartutils.error.sys import LibraryError

__all__ = []


class FlaskMiddleware(AbstractMiddleware):
    def __init__(self, plugin: AbstractMiddlewarePlugin):
        super().__init__(plugin=plugin, app_key=AppKey.FLASK)

    def __call__(self, app):
        # 装饰 Flask 应用，注册 before_request 和 after_request 钩子
        @app.before_request
        def before_request():
            # 在 Flask 里，before_request 不能获取响应对象
            # 但可以保存开始时间，或其他 request 相关信息
            flask.g._middleware_req_adapter = self.req_adapter(flask.request)
            flask.g._middleware_start = (
                asyncio.get_event_loop().time()
                if asyncio.get_event_loop().is_running()
                else None
            )

        @app.after_request
        def after_request(response):
            req_adapter = getattr(flask.g, "_middleware_req_adapter", None)
            if not req_adapter:
                raise LibraryError(
                    "flask no _middleware_req_adapter, check before_request."
                )
            req: RequestAdapter = req_adapter
            if req is None:
                req = self.req_adapter(flask.request)
            resp = self.resp_adapter(response)

            async def next_adapter():
                return resp

            # 兼容异步/同步
            if asyncio.iscoroutinefunction(self._plugin.dispatch):
                result: ResponseAdapter = asyncio.run(
                    self._plugin.dispatch(req, next_adapter)
                )
            else:
                result: ResponseAdapter = self._plugin.dispatch(req, next_adapter)  # type: ignore
            return result.response

        return app
