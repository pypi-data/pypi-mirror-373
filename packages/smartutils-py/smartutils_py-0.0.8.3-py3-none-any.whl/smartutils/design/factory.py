import sys
from abc import ABC
from collections import OrderedDict, defaultdict, deque
from typing import Callable, Generic, List, Optional, Tuple, TypeVar, final

from smartutils.error.sys import LibraryError, LibraryUsageError

K = TypeVar("K")
V = TypeVar("V")


class BaseFactory(Generic[K, V], ABC):
    # 从小达到维护顺序
    _registry_value: OrderedDict[K, V]
    _registry_order: dict[K, int]
    _registry_deps: dict[K, set[K]]

    def __init_subclass__(cls):
        cls._registry_value = OrderedDict()
        cls._registry_order = {}
        cls._registry_deps = defaultdict(set)
        cls.name = f"[{cls.__name__}]"

    @classmethod
    def _with_order(cls, key: K, order: int) -> int:

        # 插入到第一个 >= order的位置
        items = list(cls._registry_value.items())
        for insert_idx, (exist_key, _) in enumerate(items):
            exist_order = cls._registry_order.get(exist_key, -sys.maxsize)
            if order <= exist_order:
                break
        else:
            # 没有break
            insert_idx = len(items)

        cls._registry_order[key] = order

        return insert_idx

    @classmethod
    def _with_deps_all(cls):
        # 拓扑排序
        in_degrees = {k: 0 for k in cls._registry_value.keys()}
        graph = {k: [] for k in cls._registry_value.keys()}
        # 构建图
        for k, deps in cls._registry_deps.items():
            for d in deps:
                if d not in cls._registry_value:
                    raise LibraryError(  # pragma: no cover
                        f"{cls.name} require register {d} before register {k}."
                    )
                graph[d].append(k)  # 依赖项指向节点，后续需先处理完依赖项，再处理节点
                in_degrees[k] += 1  # 入度和依赖项挂钩

        # Kahn算法
        queue = deque([k for k, deg in in_degrees.items() if deg == 0])
        topo = []
        while queue:
            node = queue.popleft()  # 都已处理完依赖项
            topo.append(node)
            for neighbor in graph[node]:  # 找到依赖node的节点
                in_degrees[neighbor] -= 1  # 依赖node的节点依赖数减1
                if in_degrees[neighbor] == 0:  # 依赖node的节点没有依赖项未处理了
                    queue.append(neighbor)

        if len(topo) != len(cls._registry_value):  # 有节点的依赖项一直没处理
            raise LibraryError(f"{cls.name} deps cycle detected.")  # pragma: no cover

        # 重新整理有序字典
        new_order = OrderedDict()
        for k in topo:
            new_order[k] = cls._registry_value[k]
        cls._registry_value = new_order

    @classmethod
    def _with_deps(cls, key: K, deps: List[K]) -> int:

        # 校验依赖都已注册
        for dep in deps:
            if dep not in cls._registry_value:
                raise LibraryError(
                    f"{cls.name} require register {dep} before register {key}."
                )

        cls._registry_deps[key] = set(deps)

        items = list(cls._registry_value.items())

        # 计算所有依赖的最大位置
        dep_indices = [i for i, (k, _) in enumerate(items) if k in deps]
        return max(dep_indices) + 1

    @classmethod
    def register(
        cls,
        key: K,
        only_register_once: bool = True,
        order: Optional[int] = None,
        deps: Optional[List[K]] = None,
        check_deps: bool = False,
    ) -> Callable[[V], V]:
        """
        order越大，生效顺序越靠后；
        注意：类装饰器的注册/副作用”只会在首次 import 时发生，之后重新实例化并不会自动重新注册

        Args:
            key (K): key类
            only_register_once (bool, optional): 只能注册一次. Defaults to True.
            order (int, optional): 生效顺序. Defaults to 0.
        """
        if only_register_once and key in cls._registry_value:
            raise LibraryError(f"{cls.name} key {key} already registered.")

        if order is not None and deps is not None:
            raise LibraryError(
                f"{cls.name} key {key} order or deps, cannot set together."
            )

        def decorator(func_or_obj: V):
            if key in cls._registry_value:
                cls._registry_value[key] = func_or_obj
                return func_or_obj

            if deps is not None:
                insert_idx = cls._with_deps(key, deps)
            elif order is not None:
                insert_idx = cls._with_order(key, order)
            else:
                insert_idx = 0

            items = list(cls._registry_value.items())
            items.insert(insert_idx, (key, func_or_obj))
            cls._registry_value = OrderedDict(items)

            if deps is not None and check_deps:
                cls._with_deps_all()

            return func_or_obj

        return decorator

    @classmethod
    def get(cls, key: K) -> V:
        if key not in cls._registry_value:
            raise LibraryUsageError(f"{cls.name} key {key} not registered.")
        return cls._registry_value[key]

    @classmethod
    @final
    def all(cls) -> Tuple[Tuple[K, V], ...]:
        return tuple(cls._registry_value.items())

    @classmethod
    @final
    def reset(cls):
        cls._registry_value.clear()
        cls._registry_order.clear()
