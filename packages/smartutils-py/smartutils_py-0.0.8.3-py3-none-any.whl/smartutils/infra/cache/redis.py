from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Dict, Optional

from smartutils.config.const import ConfKey
from smartutils.config.schema.redis import RedisConf
from smartutils.ctx import CTXKey, CTXVarManager
from smartutils.design import singleton
from smartutils.error.sys import CacheError
from smartutils.infra.cache.redis_cli import AsyncRedisCli
from smartutils.infra.cache.redlock import SmartutilsInstance
from smartutils.infra.resource.manager.manager import CTXResourceManager
from smartutils.init.factory import InitByConfFactory
from smartutils.init.mixin import LibraryCheckMixin
from smartutils.log import logger

try:
    import aioredlock
    import aioredlock.redis
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    import aioredlock

__all__ = ["AsyncRedisCli", "RedisManager"]


@singleton
@CTXVarManager.register(CTXKey.CACHE_REDIS)
class RedisManager(LibraryCheckMixin, CTXResourceManager[AsyncRedisCli]):
    """
    Redis 常用命令返回值内容与类型总结（根据 tests_real/test_redis_ret_type.py 验证）：

    - 字符串/数值类：
        set/setex/psetex            -> bool          # 操作是否成功
        get/getset/getdel           -> str/None      # 字符串结果，不存在为None
        incr/incrby/decr/decrby     -> int/str       # 自增/自减后结果（通常int，部分兼容str for lua脚本场景）
        mset                        -> bool          # 操作是否成功
        mget                        -> List[str]     # 多个key的结果，没有的为None
        msetnx                      -> bool          # 表示所有都设置成功

    - set 集合相关：
        sadd/srem                   -> int           # 实际变动元素数
        scard                       -> int           # 元素数量

    - list 列表相关：
        llen/rpush/lpush            -> int           # 列表长度
        lrange                      -> List[str]     # 区间元素

    - zset 有序集合：
        zadd/zrem                   -> int           # 新增/删除数
        zcard                       -> int           # 数量
        zrange/zrangebyscore        -> List[str]     # 区间成员
        zrange(withscores=True)     -> List[Tuple[str, float]]

    - hash 字典相关：
        hset/hdel                   -> int           # 变更数
        hget                        -> str/None      # Value
        hgetall                     -> dict[str, str]# 所有字段

    - key 相关:
        delete                      -> int           # 删除key数
        exists                      -> int           # 存在key数
        expire/ttl/persist/touch    -> int/bool      # 是否成功/剩余时长/被修改key数
        type                        -> str           # 存储结构类型
        randomkey                   -> str/None      # 任意key
        scan                        -> Tuple[int | str, List[str]]    # 游标和key

    - stream 相关：
        xadd                        -> str           # 流ID
        xreadgroup/xread            -> List          # 消息对象
        xack                        -> int           # ack 成功条数

    - 脚本：
        eval/evalsha/script_load    -> 任意           # 依赖返回的lua脚本
        script_exists               -> List[bool]    # 存在性判断
        script_flush                -> None/str      # 无

    - 其它杂项及管理：
        rename/move/restore/copy    -> bool          # 是否成功
        dump                        -> bytes/None    # 序列化值
        publish                     -> int           # 订阅接收数
        pfadd/pfcount/pfmerge       -> int           # HyperLogLog 使用
        sort                        -> List[str]     # 排序结果
        slowlog_get                 -> List          # 慢日志
        slowlog_len                 -> int           # 长度
        memory_stats                -> dict          # 内存信息
        memory_usage                -> int/None      # 占用字节
        wait/save/flushall          -> int/str       # 保存/刷新响应
        info                        -> dict          # 服务器信息
        bit相关(setbit,getbit,etc)  -> int           # 位值/计数

    均通过实际用例和断言验证。
    如需新的命令类型、内容总结，请查阅redis文档或相关测试用例。
    """

    def __init__(self, confs: Optional[Dict[str, RedisConf]] = None):
        self.check(conf=confs, libs=["aioredlock"])
        assert confs

        resources = {k: AsyncRedisCli(conf, f"redis_{k}") for k, conf in confs.items()}
        self._redlock = self._init_redlock(resources)
        super().__init__(
            resources=resources,
            ctx_key=CTXKey.CACHE_REDIS,
            error=CacheError,
        )

    def _init_redlock(self, resources):
        aioredlock.redis.Instance = SmartutilsInstance
        instances = [SmartutilsInstance(r) for r in resources.values()]
        return aioredlock.Aioredlock(instances)  # type: ignore

    @property
    def curr(self) -> AsyncRedisCli:
        return super().curr

    @asynccontextmanager
    async def redlock(self, resource: str):
        """
        Redlock分布式锁异步上下文.
        用法: async with RedisManager().redlock(key):
            # do something
        """
        lock = None
        try:
            try:
                lock = await self._redlock.lock(resource)
            except Exception as e:
                logger.error(f"{self.name} redlock lock fail for {e}.")
                lock = None
            yield lock
        finally:
            if lock:
                try:
                    await self._redlock.unlock(lock)
                except Exception as e:
                    logger.exception(f"{self.name} redlock unlock fail for {e}.")


@InitByConfFactory.register(ConfKey.REDIS)
def _(conf):
    RedisManager(conf)
