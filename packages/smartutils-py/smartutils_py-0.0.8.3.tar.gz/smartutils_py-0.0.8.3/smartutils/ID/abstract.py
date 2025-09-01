from abc import ABC, abstractmethod

__all__ = ["AbstractIDGenerator"]


class AbstractIDGenerator(ABC):
    @abstractmethod
    def __next__(self):
        """
        获取下一个ID
        """
        ...

    def __iter__(self):
        """
        让生成器对象可用于 for 循环等迭代场景
        """
        return self

    def __call__(self):
        """
        使实例可直接调用生成ID
        """
        return next(self)

    @abstractmethod
    def __repr__(self) -> str: ...
