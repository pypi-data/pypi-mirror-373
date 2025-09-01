"""
26位字符
128位：48位时间戳 80位随机
唯一性比肩uuid4
无高并发限速，理论每毫秒10亿个碰撞概率0
寿命终止约10889年
"""

from datetime import datetime, timezone

import ulid

from smartutils.design import singleton
from smartutils.error.sys import LibraryUsageError
from smartutils.ID.abstract import AbstractIDGenerator
from smartutils.ID.const import IDGenType
from smartutils.ID.init import IDGen

__all__ = ["ULID", "ULIDGenerator"]


class ULID:
    """
    ULID实体对象，支持反解时间戳和随机数部分。
    """

    def __init__(self, ulid_obj):
        if isinstance(ulid_obj, str):
            self.ulid = ulid.from_str(ulid_obj)
        elif isinstance(ulid_obj, ulid.ULID):
            self.ulid = ulid_obj
        else:
            raise LibraryUsageError("ulid_obj must be str or ulid.ULID.")

        # 获取128位整数
        self.int = int(self.ulid)
        self.timestamp = self.int >> 80  # 前48位
        self.random = self.int & ((1 << 80) - 1)  # 后80位

    @property
    def milliseconds(self):
        """ULID的时间戳（自1970-01-01以来的毫秒）"""
        return self.timestamp

    @property
    def datetime(self):
        """ULID的时间戳对应的UTC时间"""
        return datetime.fromtimestamp(self.timestamp / 1000, tz=timezone.utc)

    @property
    def random_hex(self):
        """ULID的随机部分（16进制）"""
        return f"{self.random:020x}"

    @property
    def value(self):
        """ULID的128位整数值"""
        return self.int

    def __repr__(self):
        return (
            f"ULID(timestamp={self.timestamp}, random=0x{self.random:020x}, "
            f"value={self.int}, str='{str(self.ulid)}')"
        )

    @classmethod
    def parse(cls, ulid_value) -> "ULID":
        return cls(ulid_value)


@singleton
@IDGen.register(IDGenType.ULID)
class ULIDGenerator(AbstractIDGenerator):
    """
    ULID生成器，支持迭代和直接调用，返回26位字符串。
    """

    def __init__(self, **kwargs): ...

    def __next__(self):  # type: ignore
        return str(ulid.new())

    @staticmethod
    def next_ulid():
        return ulid.new()

    def __repr__(self):
        return "<ULIDGenerator()>"
