from smartutils.error.base import BaseError


class SysError(BaseError): ...


class NotFoundError(SysError):
    code = 1001
    msg = "Not Found"
    status_code = 404  # Not Found


class UnsupportedError(SysError):
    code = 1002
    msg = "Unsupported Operation"
    status_code = 405  # Method Not Allowed


class TimeOutError(SysError):
    code = 1003
    msg = "Request Timeout"
    status_code = 408  # Request Timeout


class RequestTooLargeError(SysError):
    code = 1004
    msg = "Request Too Large"
    status_code = 413  # Payload Too Large


class UnsupportedMediaTypeError(SysError):
    code = 1005
    msg = "Unsupported Media Type"
    status_code = 415  # Unsupported Media Type


class ValidationError(SysError):
    code = 1006
    msg = "Validation Error"
    status_code = 422  # Unprocessable Entity


class ExternalServiceError(SysError):
    code = 1007
    msg = "External Service Error"
    status_code = 500  # Internal Server Error


class LibraryUsageError(SysError):
    code = 1008
    msg = "Library Usage Error"
    status_code = 500  # Internal Server Error


class DatabaseError(SysError):
    code = 1009
    msg = "Database Error"
    status_code = 500  # Internal Server Error


class CacheError(SysError):
    code = 1010
    msg = "Cache Error"
    status_code = 500  # Internal Server Error


class MQError(SysError):
    code = 1011
    msg = "Message Queue Error"
    status_code = 500  # Internal Server Error


class LibraryError(SysError):
    code = 1012
    msg = "Library Error"
    status_code = 500  # Internal Server Error


class ConfigError(SysError):
    code = 1013
    msg = "Config Error"
    status_code = 500  # Internal Server Error


class NoFileError(SysError):
    code = 1014
    msg = "No File Error"
    status_code = 500


class FileError(SysError):
    code = 1015
    msg = "File Error"
    status_code = 500  # Internal Server Error


class FileInvalidError(SysError):
    code = 1016
    msg = "File Invalid Error"
    status_code = 500


class ClientError(SysError):
    code = 1017
    msg = "Client Error"
    status_code = 500  # Internal Server Error


class BreakerOpenError(SysError):
    code = 1018
    msg = "Breaker Open Error"
    status_code = 500


class UnauthorizedError(SysError):
    code = 1019
    msg = "Unauthorized Error"
    status_code = 401


class PoolOverflowError(SysError):
    code = 1020
    msg = "Pool Overflow Error"
    status_code = 500
