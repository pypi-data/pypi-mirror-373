from enum import Enum

__all__ = ["IDGenType"]


class IDGenType(Enum):
    SNOWFLAKE = "snowflake"
    UUID = "uuid"
    ULID = "ulid"
