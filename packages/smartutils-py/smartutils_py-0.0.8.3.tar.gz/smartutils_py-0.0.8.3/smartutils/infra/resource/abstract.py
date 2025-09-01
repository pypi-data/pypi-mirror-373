from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import Any, AsyncContextManager, TypeVar

__all__ = ["AbstractAsyncResource", "AbstractAsyncResourceT"]


class AbstractAsyncResource(ABC):
    @abstractmethod
    async def close(self):
        """关闭资源"""
        ...

    @abstractmethod
    async def ping(self) -> bool:
        """健康检查，返回True/False"""
        ...

    @abstractmethod
    def db(self, use_transaction: bool) -> AsyncContextManager[Any]: ...


AbstractAsyncResourceT = TypeVar("AbstractAsyncResourceT", bound=AbstractAsyncResource)


class AbstractSyncResource(ABC):
    @abstractmethod
    def close(self):
        """关闭资源"""
        ...

    @abstractmethod
    def ping(self) -> bool:
        """健康检查，返回True/False"""
        ...

    @abstractmethod
    def db(self, use_transaction: bool) -> AbstractContextManager[Any]: ...


AbstractSyncResourceT = TypeVar("AbstractSyncResourceT", bound=AbstractSyncResource)
