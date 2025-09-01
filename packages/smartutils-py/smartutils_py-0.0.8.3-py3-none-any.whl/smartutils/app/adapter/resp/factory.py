from typing import Type

from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey
from smartutils.design import BaseFactory

__all__ = ["ResponseAdapterFactory"]


class ResponseAdapterFactory(BaseFactory[AppKey, Type[ResponseAdapter]]): ...
