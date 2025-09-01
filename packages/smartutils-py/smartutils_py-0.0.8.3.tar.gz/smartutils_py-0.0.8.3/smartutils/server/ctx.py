import sys
from functools import wraps
from typing import Optional, Union, cast

from smartutils.error.sys import LibraryUsageError, TimeOutError
from smartutils.time import get_now_stamp_float, get_stamp_after

__all__ = ["Context", "timeoutd"]


class Context:
    """
    上下文对象，用于处理与超时相关的操作。

    属性:
        _start (float): 上下文创建时的时间戳（秒）。
        _deadline (Optional[float]): 超时时间点（秒），若未设置则为 None。
        timeout (Optional[float|int]): 超时时间长度（秒），可用于日志或调试。

    方法:
        timeoutd(now=None): 判断当前是否已超时。
        remain_sec(now=None): 获取距离超时时间的剩余秒数。
    """

    def __init__(
        self, sec: Optional[Union[float, int]] = None, start: Optional[float] = None
    ):
        """
        初始化 Context。

        :param sec: 超时时间（秒），可选。如果不设置则表示无超时。
        :param start: 上下文开始的时间戳（秒），可选。默认为当前时间。
        """
        self._start: float = start or get_now_stamp_float()
        self._deadline: Optional[float] = (
            get_stamp_after(self._start, second=sec) if sec else None
        )
        self.timeout = sec  # 仅用于调试和日志打印

    def timeoutd(self, now: Optional[float] = None) -> bool:
        """
        判断是否已经超时。

        :param now: 当前时间戳（秒），可选。未传则为当前系统时间。
        :return: True 表示已超时，False 表示未超时。
        """
        if self._deadline is None:
            return False

        now = now or get_now_stamp_float()
        return now >= self._deadline

    def remain_sec(self, now: Optional[float] = None) -> float:
        """
        获取距离超时时间的剩余秒数。

        :param now: 当前时间戳（秒），可选。未传则为当前系统时间。
        :return: 距离超时时间的剩余秒数。若未设置超时则为最大整数。
        """
        if self._deadline is None:
            return sys.maxsize
        now = now or get_now_stamp_float()
        return max(0, self._deadline - now)


def timeoutd(default_ret=None):
    """
    强制要求第一个参数为 Context 类型的装饰器。
    如果 ctx 超时，返回指定结果和 TimeOutError，否则正常执行函数。

    :param default_ret: 超时时返回的默认值（若为 None，则仅抛出异常）
    :return: 装饰后的函数
    """

    def _decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            if not args or not isinstance(args[0], Context):
                raise LibraryUsageError("first parameter must be Context.")

            ctx: Context = cast(Context, args[0])

            if ctx.timeoutd():
                if default_ret is not None:
                    return default_ret, TimeOutError
                return TimeOutError
            return func(*args, **kwargs)

        return decorated

    return _decorator
