from __future__ import annotations

import inspect
from functools import wraps
from typing import TYPE_CHECKING, Awaitable, Callable, Tuple, Type

from smartutils.app.adapter.middleware.abstract import (
    AbstractMiddleware,
    AbstractMiddlewarePlugin,
    chain_dispatch,
)
from smartutils.app.adapter.middleware.factory import (
    AddMiddlewareFactory,
    EndpointMiddlewareFactory,
    RouteMiddlewareFactory,
)
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey
from smartutils.error.sys import LibraryUsageError
from smartutils.log import logger

key = AppKey.FASTAPI


try:
    from fastapi import Request, Response
    from fastapi.encoders import jsonable_encoder
    from fastapi.responses import ORJSONResponse
    from fastapi.routing import APIRoute
    from starlette.middleware.base import BaseHTTPMiddleware
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import Request, Response
    from fastapi.encoders import jsonable_encoder
    from fastapi.responses import ORJSONResponse
    from fastapi.routing import APIRoute
    from starlette.middleware.base import BaseHTTPMiddleware


class StarletteMiddleware(AbstractMiddleware, BaseHTTPMiddleware):
    def __init__(self, app, plugin: AbstractMiddlewarePlugin):
        super().__init__(app=app, plugin=plugin, app_key=AppKey.FASTAPI)
        self.name = plugin.key

    async def dispatch(self, request: Request, call_next):
        logger.debug(f"{self.name} middleware dispatching request")

        # 这里拿到的，必然是Request，如果不是，框架会自动封装成Request
        req: RequestAdapter = self.req_adapter(request)

        async def next_adapter():
            response: Response = await call_next(request)
            return self.resp_adapter(response)

        resp: ResponseAdapter = await self._plugin.dispatch(req, next_adapter)
        return resp.response


@AddMiddlewareFactory.register(key)
def _(app, plugins: Tuple[AbstractMiddlewarePlugin, ...]):
    # fastapi调用顺序和add顺序相反
    for plugin in plugins[::-1]:
        app.add_middleware(StarletteMiddleware, plugin)


@RouteMiddlewareFactory.register(key)
def _(plugins: Tuple[AbstractMiddlewarePlugin, ...]) -> Type[APIRoute]:
    if not plugins:
        return APIRoute

    # TODO: 优化，这里可以考虑使用一个函数来处理, 和上面的类似，可以考虑使用一个函数来处理
    class PluginsAPIRoute(APIRoute):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        # Awaitable[Response] ≥ Coroutine[Any, Any, Response]（前者包含后者及其它实现）
        def get_route_handler(  # type: ignore
            self,
        ) -> Callable[[Request], Awaitable[Response]]:
            original_route_handler = super().get_route_handler()
            return chain_dispatch(plugins, original_route_handler)

    return PluginsAPIRoute


@EndpointMiddlewareFactory.register(key)
def _(plugins: Tuple[AbstractMiddlewarePlugin, ...]):
    # Depends实现，需要在handler里实现业务逻辑，侵入太重
    # 使用装饰器
    def decorator(endpoint_func):
        signature = inspect.signature(endpoint_func)
        param_names = list(signature.parameters.keys())

        if (
            not param_names
            or signature.parameters[param_names[0]].annotation is not Request
        ):
            raise LibraryUsageError(
                f"Endpoint `{endpoint_func.__name__}` require first param be: req: Request，"
            )

        @wraps(endpoint_func)
        async def wrapper(req: Request, *args, **kwargs):
            async def handler(_):
                ret = await endpoint_func(req, *args, **kwargs)
                if isinstance(ret, Response):
                    return ret
                return ORJSONResponse(content=jsonable_encoder(ret))

            final_handler = chain_dispatch(plugins, handler)
            return await final_handler(req)

        return wrapper

    return decorator
