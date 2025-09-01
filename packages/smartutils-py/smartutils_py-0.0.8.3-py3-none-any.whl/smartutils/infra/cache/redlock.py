import asyncio
from typing import TYPE_CHECKING

from smartutils.infra.cache.redis_cli import AsyncRedisCli

try:
    import aioredlock.redis

except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    import aioredlock.redis


class SmartutilsContextWrapper:
    """让AsyncRedisCli支持异步上下文协议，不释放、不做任何处理，仅for aioredlock兼容。"""

    def __init__(self, cli):
        self.cli = cli

    def __enter__(self):
        return self.cli

    def __exit__(self, exc_type, exc, tb): ...


class SmartutilsInstance(aioredlock.redis.Instance):
    """Instance适配层：用AsyncRedisCli动态替换aioredlock Instance，只需改__init__/connect。"""

    def __init__(self, cli: AsyncRedisCli):
        super().__init__(None)
        # connection字段沿用父类变量名，确保父类相关用法无冲突
        self.connection = cli
        self.cli = cli
        self._pool = None  # 保证父类属性表健全
        self._lock = asyncio.Lock()
        # sha1缓存等后续如父类所需，自动继承

    def __getattr__(self, name):
        return getattr(self.cli, name)

    async def connect(self):
        """
        覆写父类的连接行为，使其返回我们期望的AsyncRedisCli对象。
        保证和aioredlock父类调用with await self.connect() as redis兼容。
        """
        if self.set_lock_script_sha1 is None or self.unset_lock_script_sha1 is None:
            await self._register_scripts(self.cli)
        return SmartutilsContextWrapper(self.cli)

    async def close(self):
        await self.cli.close()
