from typing import Any

from fastapi.responses import ORJSONResponse

from smartutils.app.adapter.json_resp.factory import JsonRespFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.starlette import StarletteResponseAdapter
from smartutils.app.const import AppKey
from smartutils.error.base import BaseDataDict


class STJsonResponse(ORJSONResponse):
    def render(self, content: Any) -> bytes:
        # logger.info(content)
        # logger.info(type(content))
        return super().render(content)


@JsonRespFactory.register(AppKey.FASTAPI)
def _(data: BaseDataDict) -> ResponseAdapter:
    return StarletteResponseAdapter(
        STJsonResponse(status_code=data.status_code, content=data.data)
    )
