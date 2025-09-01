from abc import ABC, abstractmethod
from typing import Generic, Mapping, TypeVar

from smartutils.app.const import HeaderKey
from smartutils.ID import IDGen

__all__ = ["RequestAdapter"]

T = TypeVar("T")


class RequestAdapter(ABC, Generic[T]):
    def __init__(self, request: T):
        self._request: T = request

    @property
    def request(self) -> T:
        return self._request

    @abstractmethod
    def get_header(self, key: HeaderKey) -> str: ...

    @abstractmethod
    def set_header(self, key: HeaderKey, value: str): ...

    @property
    @abstractmethod
    def headers(self) -> Mapping[str, str]: ...

    @property
    @abstractmethod
    def query_params(self) -> dict: ...

    @property
    @abstractmethod
    def client_host(self) -> str: ...

    @property
    @abstractmethod
    def method(self) -> str: ...

    @property
    @abstractmethod
    def url(self) -> str: ...

    @property
    @abstractmethod
    def path(self) -> str: ...

    @abstractmethod
    def get_cookie(self, key: str) -> str: ...

    def gen_trace_id(self) -> str:
        return str(IDGen())
