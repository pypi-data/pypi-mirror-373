import sys
from typing import Optional, Set

from smartutils.infra.cache.redis import RedisManager


class RedisBitmapUtil:
    """
    通用Redis Bitmap封装。按二进制位映射对象存在性、状态等。
    """

    @classmethod
    async def set_bit(cls, key: str, offset: int, flag: bool = True) -> None:
        """
        设置bitmap中指定bit的值
        :param key: bitmap键
        :param offset: bit位（0为起点）
        :param flag: True(1)/False(0)
        """
        await RedisManager().curr.setbit(key, offset, int(flag))

    @classmethod
    async def get_bit(cls, key: str, offset: int) -> bool:
        """
        获取bitmap中指定bit的当前值
        :return: True(1)/False(0)
        """
        result = await RedisManager().curr.getbit(key, offset)
        return bool(result)

    @classmethod
    async def get_all_set_bits(
        cls, key: str, max_offset: int = sys.maxsize
    ) -> Optional[Set[int]]:
        """
        获取bitmap中所有为 1 的bit下标（即所有set用户、资源编号等）。
        :param key: bitmap键
        :param max_offset: 最大遍历bit（业务方根据ID最大值传递)
        :return: 被置1的bit集合
        """
        bitmap = await RedisManager().curr.get(key)
        if not bitmap:
            return None
        if isinstance(bitmap, str):
            # 兼容String返回
            bitmap = bitmap.encode()
        result = set()
        for byte_index, byte in enumerate(bitmap):
            if not byte:
                continue
            for bit_index in range(8):
                idx = byte_index * 8 + bit_index
                if idx > max_offset:
                    return result
                if byte & (1 << (7 - bit_index)):
                    result.add(idx)
        return result
