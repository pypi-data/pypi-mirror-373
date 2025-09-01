from __future__ import annotations

from typing import TYPE_CHECKING, Mapping

from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.factory import RequestAdapterFactory
from smartutils.app.const import AppKey, HeaderKey

try:
    from fastapi import Request
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import Request


__all__ = ["StarletteRequestAdapter"]


@RequestAdapterFactory.register(AppKey.FASTAPI)
class StarletteRequestAdapter(RequestAdapter[Request]):
    def get_header(self, key: HeaderKey) -> str:
        # 优先查 state（如果 set_header 设置过），否则查 headers
        custom_headers = getattr(self.request.state, "_custom_headers", {})
        return custom_headers.get(key) or self.request.headers.get(key) or ""

    def set_header(self, key: HeaderKey, value: str):
        # 只读不可修改
        # self.request.headers[key] = value
        if not hasattr(self.request.state, "_custom_headers"):
            self.request.state._custom_headers = {}
        self.request.state._custom_headers[key] = value

    @property
    def headers(self) -> Mapping[str, str]:
        return self.request.headers

    @property
    def query_params(self) -> dict:
        return dict(self.request.query_params)

    @property
    def client_host(self) -> str:
        return self.request.client.host if self.request.client else "-"

    @property
    def method(self) -> str:
        return self.request.method

    @property
    def url(self) -> str:
        return str(self.request.url)

    @property
    def path(self) -> str:
        return self.request.url.path

    def get_cookie(self, key: str) -> str:
        return self.request.cookies.get(key, "")
