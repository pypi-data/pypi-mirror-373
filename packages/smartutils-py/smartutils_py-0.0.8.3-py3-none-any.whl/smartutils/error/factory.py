from typing import Callable, Type

from smartutils.design import BaseFactory
from smartutils.error.base import BaseError
from smartutils.error.sys import SysError

__all__ = ["ExcErrorFactory", "ExcDetailFactory"]


class ExcErrorFactory(
    BaseFactory[Type[BaseException], Callable[[BaseException], BaseError]]
):
    @classmethod
    def get(cls, exc: BaseException) -> BaseError:  # type: ignore
        if isinstance(exc, BaseError):
            return exc

        for exc_type, trans_exc_error in cls.all():
            if isinstance(exc, exc_type):
                return trans_exc_error(exc)

        return SysError(detail=str(exc))


class ExcDetailFactory(
    BaseFactory[Type[BaseException], Callable[[BaseException], str]]
):
    @classmethod
    def get(cls, exc: BaseException) -> str:  # type: ignore
        for exc_type, handler in cls.all():
            if isinstance(exc, exc_type):
                return handler(exc)

        return str(exc)
