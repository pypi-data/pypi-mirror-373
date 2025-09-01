from abc import ABC
from typing import Any, Dict, Optional

__all__ = ["BaseError", "BaseData", "BaseDataDict", "OK"]

_DEBUG: bool = False


class BaseDataDict(dict):
    @property
    def status_code(self) -> int:
        return self.get("status_code", 200)

    @property
    def data(self) -> Dict:
        return {k: v for k, v in self.items() if k != "status_code"}


class BaseData:
    code: int
    msg: str
    status_code: int
    detail: str
    data: Any

    @property
    def as_dict(self) -> BaseDataDict:
        return BaseDataDict(
            {
                "code": self.code,
                "msg": self.msg,
                "status_code": self.status_code,
                "detail": self.detail if _DEBUG else "",
                "data": self.data,
            }
        )

    @classmethod
    def set_debug(cls, on: bool):
        global _DEBUG
        _DEBUG = on

    @property
    def is_ok(self) -> bool:
        return self.code == 0


class BaseError(Exception, ABC, BaseData):
    code = 1000
    msg = "Internal Server Error"
    status_code = 500
    detail = ""
    data = None

    def __init__(
        self,
        detail: str = "",
        code: Optional[int] = None,
        msg: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        self.code = code if code is not None else self.code
        self.msg = msg if msg is not None else self.msg
        self.status_code = status_code if status_code is not None else self.status_code
        self.detail = detail or self.detail
        super(Exception, self).__init__(self.detail)


OK = BaseError("", 0, "success", 200)
