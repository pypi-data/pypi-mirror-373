from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.factory import ResponseAdapterFactory
from smartutils.app.const import AppKey, HeaderKey

__all__ = ["FlaskResponseAdapter"]


@ResponseAdapterFactory.register(AppKey.FLASK)
class FlaskResponseAdapter(ResponseAdapter):
    def set_header(self, key: HeaderKey, value: str):
        self._response.headers[key] = value

    @property
    def status_code(self) -> int:
        return self._response.status_code

    @status_code.setter
    def status_code(self, value: int):
        self._response.status_code = value
