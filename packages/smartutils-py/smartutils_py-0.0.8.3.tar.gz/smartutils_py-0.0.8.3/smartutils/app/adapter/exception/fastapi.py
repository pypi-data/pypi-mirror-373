from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError as PydanticValidationError

from smartutils.data.base import max_int
from smartutils.error.base import BaseError
from smartutils.error.factory import ExcDetailFactory, ExcErrorFactory
from smartutils.error.mapping import HTTP_STATUS_CODE_MAP
from smartutils.error.sys import SysError, ValidationError

try:
    from fastapi.exceptions import (
        HTTPException as FastAPIHTTPException,
    )
    from fastapi.exceptions import (
        RequestValidationError,
    )
    from starlette.exceptions import HTTPException
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    from fastapi.exceptions import (
        HTTPException as FastAPIHTTPException,
    )
    from fastapi.exceptions import (
        RequestValidationError,
    )
    from starlette.exceptions import HTTPException


@ExcDetailFactory.register(PydanticValidationError)
@ExcDetailFactory.register(RequestValidationError)
def _(exc: BaseException) -> str:
    if hasattr(exc, "errors"):
        errors = getattr(exc, "errors", lambda: [])()
        msg = "\n".join(
            [
                "{loc}: {msg}".format(
                    loc=", ".join(e.get("loc", "")), msg=e.get("msg", "")
                )
                for e in errors
            ]
        )
        return msg if msg else "Param Validate Fail!"
    return "Unknown Validate Fail!"


@ExcErrorFactory.register(PydanticValidationError)
@ExcErrorFactory.register(RequestValidationError)
def _(exc: BaseException) -> BaseError:
    return ValidationError(detail=ExcDetailFactory.get(exc))


@ExcErrorFactory.register(HTTPException, order=max_int())
@ExcErrorFactory.register(FastAPIHTTPException, order=max_int())
def _(exc: BaseException) -> BaseError:
    detail = ExcDetailFactory.get(exc)
    err_cls = HTTP_STATUS_CODE_MAP.get(getattr(exc, "status_code", 0), SysError)
    return err_cls(detail=detail)
