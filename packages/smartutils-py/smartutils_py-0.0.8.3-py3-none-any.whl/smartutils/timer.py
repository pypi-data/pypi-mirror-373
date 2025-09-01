import functools
import inspect
from time import perf_counter

from smartutils.error.sys import LibraryUsageError
from smartutils.log import logger

__all__ = ["Timer", "timeit"]


class Timer:
    def __init__(self, func=perf_counter):
        self._func = func
        self._start = None
        self._elapsed = 0.0

    def start(self):
        if self._start is not None:
            raise LibraryUsageError("Timer already started.")
        self._start = self._func()

    def stop(self):
        if self._start is None:
            raise LibraryUsageError("Timer not started, call Timer().start() first.")
        end = self._func()
        self._elapsed += end - self._start
        self._start = None

    def reset(self):
        self._elapsed = 0.0
        self._start = None

    @property
    def running(self):
        return self._start is not None

    @property
    def elapsed(self):
        if self._start is not None:
            return self._elapsed + (self._func() - self._start)
        return self._elapsed

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    async def __aenter__(self):
        self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def timeit(log: str = ""):
    """
    基于 Timer 的通用计时装饰器，支持同步和异步函数。
    :param log: 日志前缀（可选）
    """

    def decorator(func):
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                async with Timer() as t:
                    result = await func(*args, **kwargs)
                logger.info(
                    "{}{} cost {:.3f}s (async)".format(log, func.__name__, t.elapsed)
                )
                return result

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                with Timer() as t:
                    result = func(*args, **kwargs)
                logger.info(
                    "{}{} cost {:.3f}s (sync)".format(log, func.__name__, t.elapsed)
                )
                return result

            return sync_wrapper

    return decorator
