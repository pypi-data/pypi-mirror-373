from enum import Enum
from typing import TypeVar

from pydantic import BaseModel

__all__ = ["ConfKey", "BaseModelT"]

BaseModelT = TypeVar("BaseModelT", bound=BaseModel)


class ConfKey(str, Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    MONGO = "mongo"
    REDIS = "redis"
    KAFKA = "kafka"
    CANAL = "canal"

    PROJECT = "project"

    LOGURU = "loguru"

    INSTANCE = "instance"

    TOKEN = "token"

    OPEN_TELEMETRY = "open_telemetry"

    GROUP_DEFAULT = "default"

    CLIENT = "client"

    ALERT_FEISHU = "alert_feishu"

    MIDDLEWARE = "middleware"

    PLACEHOLDER = "placeholder"

    PROXY = "proxy"

    # 允许注册自定义Key供测试和灵活扩展
    TEST = "__test__"
    TEST2 = "__test2__"
    TEST3 = "__test3__"
    TEST4 = "__test4__"
