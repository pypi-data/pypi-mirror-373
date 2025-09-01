from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import partial
from typing import TYPE_CHECKING, Awaitable, Callable, Dict, Optional, Tuple

import orjson

from smartutils.config.schema.client import ApiConf, ClientConf
from smartutils.infra.client.breaker import Breaker
from smartutils.infra.resource.abstract import AbstractAsyncResource
from smartutils.init.mixin import LibraryCheckMixin
from smartutils.log import logger

try:
    from httpx import AsyncClient, ConnectError, Response, TimeoutException
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    from httpx import AsyncClient, ConnectError, Response, TimeoutException


def only_connection_failures(exc):
    # 仅统计超时和连接故障
    return not isinstance(exc, (TimeoutException, ConnectError))


async def mock_response(api_conf: ApiConf, *args, **kwargs) -> Response:
    logger.info(
        f"Mocking response for API: {api_conf.method} {api_conf.path} return {api_conf.mock}"
    )
    return Response(
        status_code=200,
        content=orjson.dumps(api_conf.mock),
        headers={"Content-Type": "application/json"},
    )


class HttpClient(LibraryCheckMixin, AbstractAsyncResource):
    def __init__(self, conf: ClientConf, name: str):
        self.check(conf=conf, libs=["httpx"])

        self._conf: ClientConf = conf
        self._key = name
        self._client = AsyncClient(
            base_url=conf.endpoint,
            timeout=conf.timeout,
            verify=conf.verify_tls,
        )
        self._breaker = Breaker(name, conf, only_connection_failures)

        self._make_apis()

    def __getattr__(self, name) -> Callable[..., Awaitable[Response]]:
        attr = getattr(self._client, name)
        HTTP_METHODS = {
            "get",
            "post",
            "put",
            "patch",
            "delete",
            "options",
            "head",
            "request",
        }
        if name in HTTP_METHODS and callable(attr):

            async def _wrapped(*args, **kwargs):
                return await self._breaker.with_breaker(lambda: attr(*args, **kwargs))

            return _wrapped
        return attr

    def _make_apis(self):
        if not self._conf.apis:
            return

        apis: Dict[str, ApiConf] = self._conf.apis

        for api_name, api_conf in apis.items():
            if api_conf.mock:
                setattr(self, api_name, partial(mock_response, api_conf))
                continue

            setattr(self, api_name, partial(self._api_request, api_conf))

    async def _api_request(self, api_conf: ApiConf, *args, **kwargs) -> Response:
        async def _do_request():
            kwargs["timeout"] = (
                kwargs.pop("timeout", None) or api_conf.timeout or self._conf.timeout
            )
            resp = await self._client.request(
                api_conf.method,
                api_conf.path,
                *args,
                **kwargs,
            )
            return resp

        return await self._breaker.with_breaker(_do_request)

    def check_resp(self, resp: Response) -> Tuple[Optional[Dict], Optional[str]]:
        if resp.status_code != 200:
            return None, f"return {resp.status_code}."

        try:
            data = resp.json()
        except ValueError:
            return None, f"return data not json. {resp.text}."

        if "code" not in data:
            return None, f"code not found {data}."

        if data["code"] != 0:
            return None, f"code not 0 {data}."

        if "data" not in data:
            return None, f"data not found {data}."

        return data["data"], None

    async def close(self):
        await self._client.aclose()

    async def ping(self) -> bool:
        try:
            resp = await self._client.get("/")
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"{self.name} Ping failed {e}")
            return False

    @asynccontextmanager
    async def db(self, use_transaction: bool) -> AsyncGenerator["HttpClient", None]:
        yield self
