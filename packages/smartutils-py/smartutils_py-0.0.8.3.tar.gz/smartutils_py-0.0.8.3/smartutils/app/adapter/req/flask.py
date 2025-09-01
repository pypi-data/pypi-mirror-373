from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.adapter.req.factory import RequestAdapterFactory
from smartutils.app.const import AppKey, HeaderKey

__all__ = ["FlaskRequestAdapter"]


@RequestAdapterFactory.register(AppKey.FLASK)
class FlaskRequestAdapter(RequestAdapter):
    def get_header(self, key: HeaderKey) -> str:
        return self.request.headers.get(key)

    def set_header(self, key: HeaderKey, value: str):
        self.request.headers[key] = value

    @property
    def headers(self):
        return self.request.headers

    @property
    def query_params(self):
        return self.request.args

    @property
    def client_host(self):
        return self.request.remote_addr or "-"

    @property
    def method(self):
        return self.request.method

    @property
    def url(self):
        return self.request.url

    def get_cookie(self, key: str) -> str:
        return self.request.cookies.get(key)
