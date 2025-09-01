from enum import Enum

__all__ = ["CTXKey"]


class CTXKey(str, Enum):
    CACHE_REDIS = "cache_redis"

    DB_MYSQL = "db_mysql"
    DB_POSTGRESQL = "db_postgresql"
    DB_MONGO = "db_mongo"

    MQ_KAFKA = "mq_kafka"

    CLIENT = "client"

    ALERT_FEISHU = "alert_feishu"

    TRACE_ID = "traceid"
    USERID = "userid"
    USERNAME = "username"
    PERMISSION_USER_IDS = "permission_user_ids"

    LOGGER_LOGURU = "logger_loguru"

    TIMER = "timer"
