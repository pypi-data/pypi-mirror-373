from __future__ import annotations

import difflib
from enum import Enum
from typing import Any, Dict, Optional, Type, TypeVar

from smartutils.error.sys import LibraryUsageError

__all__ = ["LowStr", "EnumMapBase"]


M = TypeVar("M")  # 映射类型（如bool、str、int等）
E = TypeVar("E", bound="EnumMapBase")


class EnumMapBase(Enum):
    """
    支持与任意类型(如bool、str、int、对象等)的静态双向映射的抽象枚举基类。
    """

    @classmethod
    def _obj_map(cls: Type[E]) -> Dict[E, M]:  # type: ignore
        """
        返回 枚举成员对象 => 映射值 的静态映射表，需在子类实现
        """
        raise LibraryUsageError("Subclasses must implement _obj_map.")

    @classmethod
    def _mapped_obj_map(cls: Type[E]) -> Dict[M, E]:  # type: ignore
        """
        构造 映射值 => 枚举成员 的静态映射表（反向查找）
        """
        if not hasattr(cls, "_reverse_map_cache"):
            forward = cls._obj_map()
            reverse: Dict[M, E] = {v: k for k, v in forward.items()}
            setattr(cls, "_reverse_map_cache", reverse)
        return getattr(cls, "_reverse_map_cache")

    @property
    def mapped(self: E) -> M:  # type: ignore
        """
        获取当前枚举成员对应的映射值，如True/False或其他类型。
        """
        return self._obj_map()[self]

    @classmethod
    def from_mapped(cls: Type[E], mapped_val: M) -> E:  # type: ignore
        """
        从映射值获取对应的枚举成员，若不存在则抛出KeyError
        """
        return cls._mapped_obj_map()[mapped_val]

    @classmethod
    def from_mapped_fuzzy(cls, mapped_fuzzy: str, cutoff: float = 0.6) -> Optional[E]:  # type: ignore
        """
        支持映射值的模糊查找（如匹配类似的字符串/标签等），找到最接近的对应枚举成员。
        适用于映射表的value为str类型。返回第一个高匹配度结果，否则None。
        """
        mapped_map = cls._mapped_obj_map()
        matches = difflib.get_close_matches(
            mapped_fuzzy, mapped_map.keys(), n=1, cutoff=cutoff
        )
        if not matches:
            return None
        return mapped_map[matches[0]]  # type: ignore

    @classmethod
    def try_from_mapped(cls: Type[E], mapped_val: M) -> Optional[E]:  # type: ignore
        """
        安全获取：从映射值返回枚举成员，若不存在则返回None
        """
        return cls._mapped_obj_map().get(mapped_val)

    @classmethod
    def mapped_list(cls: Type[E]) -> list[M]:  # type: ignore
        """
        返回所有的映射值列表
        """
        return [cls._obj_map()[m] for m in cls]

    @classmethod
    def obj_list(cls: Type[E]) -> list[E]:
        """
        返回所有的枚举成员列表
        """
        return list(cls._obj_map().keys())

    @classmethod
    def mapped_dict(cls: Type[E]) -> Dict[E, M]:  # type: ignore
        """
        返回完整枚举成员到映射值的dict
        """
        return dict(cls._obj_map())

    @classmethod
    def mapped_dict_str(cls) -> str:
        """
        以[基础类型: 映射值]形式美观打印全部映射。
        例如：1: 未设置, 20: 全部, ...
        """
        return ", ".join(f"{m.value}: {v}" for m, v in cls.mapped_dict().items())

    @classmethod
    def from_any(cls: Type[E], value: Any) -> E:
        """
        可接受Enum自身、映射值、字符串等，并返回Enum成员。
        """
        if isinstance(value, cls):
            return value
        mapped_map = cls._mapped_obj_map()
        if value in mapped_map:
            return mapped_map[value]
        raise ValueError(f"无法从{value}映射到{cls.__name__}")


class LowStr(str):
    def __new__(cls, s: str):
        return str.__new__(cls, s.lower())


class SharedData:
    _data = {}

    @classmethod
    def set(cls, key, value):
        cls._data[key] = value

    @classmethod
    def get(cls, key, default=None) -> Any:
        return cls._data.get(key, default)

    @classmethod
    def get_or_set(cls, key, default) -> Any:
        value = cls.get(key)
        if value:
            return value

        if default:
            value = default

        if value:
            cls.set(key, value)

        return value
