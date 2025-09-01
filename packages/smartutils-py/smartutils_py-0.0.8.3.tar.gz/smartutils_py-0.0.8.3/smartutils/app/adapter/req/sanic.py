from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.factory import RequestAdapterFactory
from smartutils.app.const import AppKey, HeaderKey

__all__ = ["SanicRequestAdapter"]


@RequestAdapterFactory.register(AppKey.SANIC)
class SanicRequestAdapter(RequestAdapter):
    def get_header(self, key: HeaderKey) -> str:
        return self.request.headers.get(key)

    def set_header(self, key: HeaderKey, value: str):
        self.request.headers[key] = value

    @property
    def headers(self) -> dict:
        # Sanic request.headers 是 CIMultiDict，支持 dict 行为
        return self.request.headers

    @property
    def query_params(self) -> dict:
        # Sanic request.args 是 MultiDict，支持 dict 行为
        return self.request.args

    @property
    def client_host(self) -> str:
        # Sanic request.remote_addr 是客户端 IP
        return self.request.remote_addr

    @property
    def method(self) -> str:
        return self.request.method

    @property
    def url(self) -> str:
        # Sanic 没有完整 url 属性，可拼接
        return str(self.request.url)

    def get_cookie(self, key: str) -> str:
        return self.request.cookies.get(key)
