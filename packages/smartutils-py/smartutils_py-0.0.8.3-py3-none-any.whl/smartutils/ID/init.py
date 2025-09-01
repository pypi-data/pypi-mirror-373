from typing import Callable, Optional, Tuple, Type

from smartutils.design import BaseFactory
from smartutils.error.sys import LibraryUsageError
from smartutils.ID.abstract import AbstractIDGenerator
from smartutils.ID.const import IDGenType


class _IDGen(
    AbstractIDGenerator,
    BaseFactory[IDGenType, Tuple[Callable[..., AbstractIDGenerator], bool]],
):
    def __init__(self):
        self._gen: Optional[AbstractIDGenerator] = None
        self._type: Optional[IDGenType] = None

    @classmethod
    def register(cls, id_type: IDGenType, need_conf: bool = False, **kwargs):  # type: ignore
        def decorator(gen_cls: Type[AbstractIDGenerator]) -> Type[AbstractIDGenerator]:
            super(_IDGen, cls).register(id_type, **kwargs)((gen_cls, need_conf))
            return gen_cls

        return decorator

    def init(self, id_gen_type: IDGenType = IDGenType.ULID, conf=None):
        gen_cls, need_conf = self.get(id_gen_type)
        self._type = id_gen_type
        if need_conf:
            if not conf:
                raise LibraryUsageError(f"IDGen {gen_cls} need conf.")
            self._gen = gen_cls(**conf.kw)
        else:
            self._gen = gen_cls()

    def __next__(self):
        if self._gen is None:
            raise LibraryUsageError("IDGen need init, call IDGen.init(...) first.")
        return self._gen()

    def __repr__(self):
        return f"<IDGen(type={self._type})>"


IDGen = _IDGen()

__all__ = ["IDGen", "IDGenType"]
