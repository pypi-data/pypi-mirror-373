from smartutils.app.adapter.middleware.abstract import (
    AbstractMiddleware,
    AbstractMiddlewarePlugin,
)
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey
from smartutils.error.sys import LibraryError

__all__ = []


class SanicMiddleware(AbstractMiddleware):
    def __init__(self, plugin: AbstractMiddlewarePlugin):
        super().__init__(plugin=plugin, app_key=AppKey.SANIC)

    def __call__(self, app):
        # Sanic 的中间件是 async def(request) or async def(request, response)
        @app.middleware("request")
        async def before_request(request):
            # 保存适配器到 request.ctx
            request.ctx._req_adapter = self.req_adapter(request)

        @app.middleware("response")
        async def after_response(request, response):
            req_adapter = getattr(request.ctx, "_req_adapter", None)
            if not req_adapter:
                raise LibraryError(
                    "sanic no _middleware_req_adapter, check before_request."
                )
            req: RequestAdapter = req_adapter
            if req is None:
                req = self.req_adapter(request)
            resp = self.resp_adapter(response)

            async def next_adapter():
                return resp

            # 调用插件
            result: ResponseAdapter = await self._plugin.dispatch(req, next_adapter)
            return result.response

        return app
