from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.factory import ResponseAdapterFactory
from smartutils.app.const import AppKey, HeaderKey

__all__ = ["TornadoResponseAdapter"]


@ResponseAdapterFactory.register(AppKey.TORNADO)
class TornadoResponseAdapter(ResponseAdapter):
    def set_header(self, key: HeaderKey, value: str):
        self._response.set_header(key, value)

    @property
    def status_code(self) -> int:
        return self._response.get_status()

    @status_code.setter
    def status_code(self, value: int):
        self._response.set_status(value)
