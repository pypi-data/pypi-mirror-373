from smartutils.app.adapter.middleware.abstract import (
    AbstractMiddleware,
    AbstractMiddlewarePlugin,
)
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey

__all__ = []


class DjangoMiddleware(AbstractMiddleware):
    def __init__(self, plugin: AbstractMiddlewarePlugin):
        super().__init__(plugin=plugin, app_key=AppKey.DJANGO)

    def __call__(self, get_response):
        # 检查是否异步视图
        import asyncio

        is_async = asyncio.iscoroutinefunction(get_response)

        if is_async:

            async def async_middleware(request):
                req: RequestAdapter = self.req_adapter(request)

                async def next_adapter():
                    response = await get_response(request)
                    return self.resp_adapter(response)

                resp: ResponseAdapter = await self._plugin.dispatch(req, next_adapter)
                return resp.response

            return async_middleware
        else:

            def sync_middleware(request):
                req: RequestAdapter = self.req_adapter(request)

                async def next_adapter():
                    response = get_response(request)
                    return self.resp_adapter(response)

                import asyncio

                resp: ResponseAdapter = asyncio.run(
                    self._plugin.dispatch(req, next_adapter)
                )
                return resp.response

            return sync_middleware
