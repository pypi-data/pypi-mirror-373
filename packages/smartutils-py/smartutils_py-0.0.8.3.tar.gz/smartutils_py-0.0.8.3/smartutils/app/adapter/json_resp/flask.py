from __future__ import annotations

from typing import TYPE_CHECKING

try:
    from flask import jsonify
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    from flask import jsonify


from smartutils.app.adapter.json_resp.factory import JsonRespFactory
from smartutils.app.adapter.resp.abstract import ResponseAdapter
from smartutils.app.adapter.resp.flask import FlaskResponseAdapter
from smartutils.app.const import AppKey
from smartutils.error.base import BaseDataDict


@JsonRespFactory.register(AppKey.FLASK)
def _(data: BaseDataDict) -> ResponseAdapter:
    response = jsonify(data.data)
    response.status_code = data.status_code
    return FlaskResponseAdapter(response)
