import sys
from enum import Enum, IntEnum

from smartutils.data import SharedData

__all__ = [
    "HeaderKey",
    "AppKey",
    "MiddlewarePluginOrder",
]


class HeaderKey(str, Enum):
    X_USER_ID = "X-User-Id"
    X_USER_NAME = "X-User-Name"
    X_TRACE_ID = "X-Trace-ID"
    X_P_USER_IDS = "X-P-User-Ids"
    X_ECHO = "X-Echo"


class AppKey(Enum):
    AIOHTTP = "aiohttp"
    DJANGO = "django"
    FLASK = "flask"
    SANIC = "sanic"
    FASTAPI = "fastapi"
    TORNADO = "tornado"

    @classmethod
    def list(cls):
        return [e.value for e in cls]


class MiddlewarePluginOrder(IntEnum):
    # 按值顺序，从小到大，依次处理请求
    ECHO = -sys.maxsize
    ME = -sys.maxsize + 10
    APIKEY = -sys.maxsize + 20
    PERMISSION = -sys.maxsize + 30
    HEADER = -100
    LOG = 100
    EXCEPTION = sys.maxsize


class RunEnv(SharedData):
    @classmethod
    def set_conf_path(cls, path: str):
        cls.set("conf", path)

    @classmethod
    def get_conf_path(cls, default=None) -> str:
        return cls.get("conf", default)

    @classmethod
    def set_app(cls, app: AppKey):
        cls.set("app", app)

    @classmethod
    def get_app(cls) -> AppKey:
        return cls.get("app")
