from time import perf_counter
from typing import Awaitable, Callable

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import MiddlewarePluginOrder
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.config.schema.middleware import MiddlewarePluginKey
from smartutils.design import SingletonMeta
from smartutils.log import logger

__all__ = ["LogPlugin"]


@MiddlewarePluginFactory.register(
    MiddlewarePluginKey.LOG, order=MiddlewarePluginOrder.LOG
)
class LogPlugin(AbstractMiddlewarePlugin, metaclass=SingletonMeta):

    async def dispatch(
        self,
        req: RequestAdapter,
        next_adapter: Callable[[], Awaitable[ResponseAdapter]],
    ) -> ResponseAdapter:
        start = perf_counter()
        logger.debug(
            "{client} - '{method} {url}' - Query: {query}",
            client=req.client_host,
            method=req.method,
            url=req.url,
            query=req.query_params,
        )
        resp: ResponseAdapter = await next_adapter()

        cost = (perf_counter() - start) * 1000
        logger.info(
            "{client} - '{method} {url}' - Query: {query} Status: {code} - Cost: {cost:.3f} ms",
            client=req.client_host,
            method=req.method,
            url=req.url,
            query=req.query_params,
            code=resp.status_code,
            cost=cost,
        )
        return resp
