"""
36位字符，随机128位

安全性高
无序、长度长，不利存储
百万级/s
无寿命终止
"""

import uuid

from smartutils.design import singleton
from smartutils.ID.abstract import AbstractIDGenerator
from smartutils.ID.const import IDGenType
from smartutils.ID.init import IDGen

__all__ = ["UUIDGenerator"]


@singleton
@IDGen.register(IDGenType.UUID)
class UUIDGenerator(AbstractIDGenerator):
    """
    UUID生成器，支持迭代和直接调用，每次生成一个新的UUID字符串
    """

    def __init__(self, **kwargs): ...

    def __next__(self):  # type: ignore
        return str(uuid.uuid4())

    @staticmethod
    def next_uuid():
        return uuid.uuid4()

    def __repr__(self):
        return "<UUIDGenerator()>"
