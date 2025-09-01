from smartutils.app.adapter.middleware.abstract import (
    AbstractMiddleware,
    AbstractMiddlewarePlugin,
)
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey

__all__ = []


class TornadoMiddleware(AbstractMiddleware):
    def __init__(self, plugin: AbstractMiddlewarePlugin):
        super().__init__(plugin=plugin, app_key=AppKey.TORNADO)

    def __call__(self, app):
        # patch 原始 Application.__call__
        original_call = app.__call__

        async def patched_call(request):
            req: RequestAdapter = self.req_adapter(request)

            async def next_adapter():
                response = await original_call(request)
                return self.resp_adapter(response)

            resp: ResponseAdapter = await self._plugin.dispatch(req, next_adapter)
            return resp.response

        app.__call__ = patched_call
        return app
