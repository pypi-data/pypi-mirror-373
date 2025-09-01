from datetime import timedelta
from typing import TYPE_CHECKING, Any, Callable

from smartutils.config.schema.breaker import BreakerConf
from smartutils.error.sys import BreakerOpenError
from smartutils.init.mixin import LibraryCheckMixin

try:
    from aiobreaker import CircuitBreaker, CircuitBreakerError
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    from aiobreaker import CircuitBreaker, CircuitBreakerError


class Breaker(LibraryCheckMixin):
    def __init__(
        self, name: str, conf: BreakerConf, exclude_exc: Callable[[Exception], bool]
    ):
        self.check(libs=["aiobreaker"], conf=conf)

        self._breaker = None
        self._name = f"client_breaker_{name}"
        if conf.breaker_enabled:
            self._breaker = CircuitBreaker(
                fail_max=conf.breaker_fail_max,
                timeout_duration=timedelta(conf.breaker_reset_timeout),
                name=self._name,
                exclude=(exclude_exc,),
            )

    async def with_breaker(self, func, *args, **kwargs) -> Any:
        """
        func: 异步函数(未调用)
        args/kwargs: 传给func
        """
        if self._breaker is None:
            return await func(*args, **kwargs)
        try:
            return await self._breaker.call_async(func, *args, **kwargs)
        except CircuitBreakerError:
            raise BreakerOpenError(
                f"Circuit breaker is OPEN for this client {self._name}!"
            )
