from __future__ import annotations

import importlib
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import partial
from typing import TYPE_CHECKING, Awaitable, Callable, Optional

from smartutils.config.schema.client import ClientConf
from smartutils.infra.client.breaker import Breaker
from smartutils.infra.resource.abstract import AbstractAsyncResource
from smartutils.init.mixin import LibraryCheckMixin

try:
    import grpc
    import grpc.aio
    from google.protobuf.message import Message
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    import grpc
    import grpc.aio
    from google.protobuf.message import Message


def only_grpc_unavailable_or_timeout(exc):
    # 只计入“服务不可用”和“超时”
    if isinstance(exc, grpc.aio.AioRpcError):
        code = exc.code()
        return code not in (
            grpc.StatusCode.UNAVAILABLE,
            grpc.StatusCode.DEADLINE_EXCEEDED,
        )
    return True


class GrpcClient(LibraryCheckMixin, AbstractAsyncResource):
    def __init__(self, conf: ClientConf, name: str):
        self.check(conf=conf, libs=["grpc"])

        self._conf: ClientConf = conf
        self._name = name

        if conf.tls:
            if not conf.verify_tls:
                # TODO：不验证证书
                creds = grpc.ssl_channel_credentials()
            else:
                creds = grpc.ssl_channel_credentials()

            self._channel = grpc.aio.secure_channel(conf.endpoint, creds)
        else:
            self._channel = grpc.aio.insecure_channel(conf.endpoint)

        self._breaker = Breaker(name, conf, only_grpc_unavailable_or_timeout)

        self._make_apis()

    def _make_apis(self):
        if not self._conf.apis:
            return

        for api_name, api_conf in self._conf.apis.items():
            func = self._get_stub_func(api_conf.path, api_conf.method)
            setattr(
                self,
                api_name,
                partial(self._api_request, func, api_conf.timeout),
            )

    def _get_stub_func(self, path, method: str):
        if isinstance(path, str):
            module_path, cls_name = path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            path = getattr(module, cls_name)

        stub = path(self._channel)
        return getattr(stub, method)

    async def _api_request(self, func, api_timeout: Optional[int], *args, **kwargs):
        async def _do_request():
            kwargs["timeout"] = (
                kwargs.pop("timeout", None) or api_timeout or self._conf.timeout
            )
            return await func(*args, **kwargs)

        return await self._breaker.with_breaker(_do_request)

    async def request(self, path, method, *args, **kwargs):
        func = self._get_stub_func(path, method)
        return await self._api_request(func, None, *args, **kwargs)

    async def close(self):
        await self._channel.close()

    async def ping(self) -> bool:
        # 如果服务端实现了健康检查api，可自定义，这里用gRPC channel ready简示
        try:
            await self._channel.channel_ready()
            return True
        except Exception:
            return False

    @asynccontextmanager
    async def db(self, use_transaction: bool) -> AsyncGenerator["GrpcClient", None]:
        yield self

    def __getattr__(self, name) -> Callable[..., Awaitable[Message]]:
        # ide不报错
        return getattr(self, name)
