from smartutils.error.base import BaseError


class BizError(BaseError):
    code = 2000
    msg = "Business Error"
    status_code = 400


class NotFoundError(BizError):
    code = 2001
    msg = "Not Found"
    status_code = 404


class ConflictError(BizError):
    code = 2002
    msg = "Conflict"
    status_code = 409
