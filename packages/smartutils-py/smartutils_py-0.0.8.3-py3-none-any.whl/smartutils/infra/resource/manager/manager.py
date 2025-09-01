from __future__ import annotations

import asyncio
import functools
from abc import ABC
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    Union,
    overload,
)

from smartutils.call import call_hook
from smartutils.config.const import ConfKey
from smartutils.ctx import CTXKey, CTXVarManager
from smartutils.design import MyBase
from smartutils.error.base import BaseError
from smartutils.error.sys import LibraryUsageError, SysError
from smartutils.infra.resource.abstract import AbstractAsyncResourceT
from smartutils.log import logger

__all__ = ["ResourceManagerRegistry", "CTXResourceManager"]


class ResourceManagerRegistry:
    _instances: List[CTXResourceManager] = []

    @classmethod
    def register(cls, instance):
        cls._instances.append(instance)

    @classmethod
    def get_all(cls):
        return list(cls._instances)

    @classmethod
    async def close_all(cls):
        await asyncio.gather(*(mgr.close() for mgr in cls.get_all()))

    @classmethod
    def reset_all(cls):
        for mgr in cls.get_all():
            mgr.reset()


class CTXResourceManager(MyBase, Generic[AbstractAsyncResourceT], ABC):
    def __init__(
        self,
        *,
        resources: Dict[str, AbstractAsyncResourceT],
        ctx_key: CTXKey,
        success: Optional[Callable[..., Any]] = None,
        fail: Optional[Callable[..., Any]] = None,
        error: Optional[Type[SysError]] = None,
        **kwargs,
    ):
        self._ctx_key: CTXKey = ctx_key
        self._resources = resources
        self._success = success
        self._fail = fail
        self._error = error if error else SysError
        ResourceManagerRegistry.register(self)
        super().__init__(**kwargs)

        logger.info("Initialized {name}.", name=self.name)

    def __str__(self) -> str:
        return self.name

    def _check_key(self, key):
        if key not in self._resources:
            raise LibraryUsageError(f"{self.name} require {key} in config.yaml.")

    def _build_wrapper(self, func, key, use_transaction: bool = False):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            self._check_key(key)
            resource = self._resources[key]
            async with resource.db(use_transaction=use_transaction) as session:
                with CTXVarManager.use(self._ctx_key, session):
                    try:
                        result = await func(*args, **kwargs)
                        await call_hook(self._success, session)
                        return result
                    except BaseError as e:
                        raise e
                    except Exception as e:
                        logger.exception(f"{self.name} fail")
                        await call_hook(self._fail, session)
                        raise self._error(f"{self.name} fail: {e}") from None

        return wrapper

    @overload
    def use(
        self, arg: None = ..., *, use_transaction: bool = False
    ) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]: ...
    @overload
    def use(
        self, arg: str, *, use_transaction: bool = False
    ) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]: ...
    @overload
    def use(
        self, arg: Callable[..., Awaitable[Any]], *, use_transaction: bool = False
    ) -> Callable[..., Awaitable[Any]]: ...

    def use(
        self,
        arg: Optional[Union[str, Callable[..., Awaitable[Any]]]] = None,
        *,
        use_transaction: bool = False,
    ) -> Any:
        """支持以下三种调用方式：
        use()
        use
        use(ConfKey.xxx)
        use(use_transaction=False)
        """
        # 支持 @mgr.use
        if callable(arg):
            func = arg
            key = ConfKey.GROUP_DEFAULT
            return self._build_wrapper(func, key, use_transaction=use_transaction)

        # 支持 @mgr.use() 或 @mgr.use('key')
        def decorator(
            func: Callable[..., Awaitable[Any]],
        ) -> Callable[..., Awaitable[Any]]:
            key = arg if isinstance(arg, str) and arg else ConfKey.GROUP_DEFAULT
            return self._build_wrapper(func, key, use_transaction=use_transaction)

        return decorator

    @property
    def curr(self):
        try:
            return CTXVarManager.get(self._ctx_key)
        except LibraryUsageError:
            raise LibraryUsageError(f"Must call {self.name}.use(...) first.") from None

    def client(self, key: str = ConfKey.GROUP_DEFAULT) -> AbstractAsyncResourceT:
        self._check_key(key)
        return self._resources[key]

    async def close(self):
        for key, cli in self._resources.items():
            try:
                await cli.close()
            except:  # noqa
                logger.exception(f"{self.name} Failed to close {self} {key}")

    async def health_check(self) -> Dict[str, bool]:
        result = {}
        for key, cli in self._resources.items():
            result[key] = await cli.ping()
        return result

    def reset(self):
        self._resources = {}
