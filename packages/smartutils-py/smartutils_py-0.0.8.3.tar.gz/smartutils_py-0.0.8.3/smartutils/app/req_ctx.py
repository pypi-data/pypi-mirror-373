from typing import List, Optional

from smartutils.ctx import CTXKey, CTXVarManager

__all__ = ["ReqCTX"]


class ReqCTX:
    @classmethod
    def get_userid(cls) -> int:
        """
        获取当前用户ID，若用户未登录，则为0
        """
        return CTXVarManager.get(CTXKey.USERID, 0)

    @classmethod
    def get_username(cls) -> str:
        """
        获取当前用户名，若用户未登录，则为空字符穿
        """
        return CTXVarManager.get(CTXKey.USERNAME, "")

    @classmethod
    def get_traceid(cls) -> str:
        """
        获取当前追踪ID
        """
        return CTXVarManager.get(CTXKey.TRACE_ID, "")

    @classmethod
    def get_permission_user_ids(cls) -> Optional[List[int]]:
        """
        获取当前用户，有权限访问的用户的ID列表，返回None表示无限制，返回数组则只能访问数组中的用户ID的数据
        """
        return CTXVarManager.get(CTXKey.PERMISSION_USER_IDS, return_none=True)
