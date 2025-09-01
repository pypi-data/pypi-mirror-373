from types import MappingProxyType

from smartutils.error.sys import (
    SysError,
    ValidationError,
    UnsupportedMediaTypeError,
    UnsupportedError,
    RequestTooLargeError,
    TimeOutError,
    NotFoundError,
)

HTTP_STATUS_CODE_MAP = MappingProxyType(
    {
        400: ValidationError,
        401: ValidationError,
        403: ValidationError,
        404: NotFoundError,
        405: UnsupportedError,
        408: TimeOutError,
        413: RequestTooLargeError,
        415: UnsupportedMediaTypeError,
        422: ValidationError,
        500: SysError,
    }
)
