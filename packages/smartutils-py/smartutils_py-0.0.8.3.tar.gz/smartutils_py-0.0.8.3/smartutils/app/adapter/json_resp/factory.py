from typing import Callable

from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.const import AppKey
from smartutils.design import BaseFactory
from smartutils.error.base import BaseDataDict

__all__ = ["JsonRespFactory"]


class JsonRespFactory(
    BaseFactory[AppKey, Callable[[BaseDataDict], ResponseAdapter]]
): ...
