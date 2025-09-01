from __future__ import annotations

from typing import TYPE_CHECKING

from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.factory import ResponseAdapterFactory
from smartutils.app.const import AppKey, HeaderKey

try:
    from fastapi import Response
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import Response


__all__ = ["StarletteResponseAdapter"]


@ResponseAdapterFactory.register(AppKey.FASTAPI)
class StarletteResponseAdapter(ResponseAdapter[Response]):
    def set_header(self, key: HeaderKey, value: str):
        self._response.headers[key] = value

    @property
    def status_code(self) -> int:
        return self._response.status_code

    @status_code.setter
    def status_code(self, value: int):
        self._response.status_code = value
