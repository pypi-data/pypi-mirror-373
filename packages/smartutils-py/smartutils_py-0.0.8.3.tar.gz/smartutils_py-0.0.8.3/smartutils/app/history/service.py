from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from smartutils.app.history.model import OpHistory, OpType
from smartutils.design import singleton
from smartutils.infra import MySQLManager

try:
    from sqlalchemy import asc, desc, func, or_, select
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy import asc, desc, func, or_, select


def get_db() -> MySQLManager:
    return MySQLManager()


__all__ = ["op_history_controller", "BizOpInfo"]


@dataclass
class OpUser:
    creator_id: Optional[int] = None
    updator_id: Optional[int] = None


@singleton
class OpHistoryController:
    @classmethod
    async def record_history(
        cls,
        biz_type: str,
        biz_id: int,
        op_type: OpType,
        op_id: int,
        before: Optional[Dict[str, Any]] = None,
        after: Optional[Dict[str, Any]] = None,
        remark: Optional[str] = None,
    ):
        """
        写入一条操作历史记录
        """
        op = OpHistory(
            biz_type=biz_type,
            biz_id=biz_id,
            op_type=op_type.value,
            op_id=op_id,
            before_data=before or {},
            after_data=after or {},
            remark=remark,
        )
        get_db().curr.add(op)

    @classmethod
    async def get_op_id_by_order(
        cls,
        biz_type: str,
        biz_ids: List[int],
        order: str = "asc",
        op_type: Optional[OpType] = None,
    ) -> Dict[int, int]:
        """
        根据排序方式获取每个biz_id首条（asc）或末条（desc）的操作人id
        对应sql：
        SELECT biz_id, op_id
        FROM (
            SELECT
                biz_id,
                op_id,
                ROW_NUMBER() OVER (PARTITION BY biz_id ORDER BY op_time ASC/DESC, id ASC/DESC) AS rn
            FROM op_history
            WHERE biz_type = 'xxx' AND biz_id IN (1,2,3,...)
        ) t
        WHERE rn = 1
        """
        if not biz_ids:
            return {}

        if order == "asc":
            order_by = [asc(OpHistory.op_time), asc(OpHistory.id)]
        else:
            order_by = [desc(OpHistory.op_time), desc(OpHistory.id)]

        row_number = (
            func.row_number()
            .over(partition_by=OpHistory.biz_id, order_by=order_by)
            .label("rn")
        )

        condition = [
            OpHistory.biz_type == biz_type,
            OpHistory.biz_id.in_(biz_ids),
        ]
        if op_type is not None:
            condition.append(OpHistory.op_type == op_type.value)
        stmt = (
            select(OpHistory.biz_id, OpHistory.op_id)
            .where(*condition)
            .add_columns(row_number)
        )
        sub_q = stmt.subquery()
        outer_stmt = select(sub_q.c.biz_id, sub_q.c.op_id).where(sub_q.c.rn == 1)
        result = await get_db().curr.execute(outer_stmt)
        return {biz_id: op_id for biz_id, op_id in result.fetchall()}

    @classmethod
    async def get_creator_id(cls, biz_type: str, biz_ids: List[int]) -> Dict[int, int]:
        return await cls.get_op_id_by_order(
            biz_type, biz_ids, order="asc", op_type=OpType.ADD
        )

    @classmethod
    async def get_last_updator_id(
        cls, biz_type: str, biz_ids: List[int]
    ) -> Dict[int, int]:
        return await cls.get_op_id_by_order(
            biz_type, biz_ids, order="desc", op_type=OpType.UPDATE
        )

    @classmethod
    async def get_creator_and_last_updator_id(
        cls, biz_type: str, biz_ids: List[int]
    ) -> Dict[int, OpUser]:
        """
        一次性获取每个biz_id的创建人（op_type=1最早的）和最后修改人（op_type=3最新的）
        返回: {biz_id: {'creator': op_id, 'last_updator': op_id}}
        """
        if not biz_ids:
            return {}

        # row_number: 最早的op_type=1，最新的op_type=3
        creator_row_num = (
            func.row_number()
            .over(
                partition_by=OpHistory.biz_id,
                order_by=[asc(OpHistory.op_time), asc(OpHistory.id)],
            )
            .label("creator_rn")
        )
        updator_row_num = (
            func.row_number()
            .over(
                partition_by=OpHistory.biz_id,
                order_by=[desc(OpHistory.op_time), desc(OpHistory.id)],
            )
            .label("updator_rn")
        )

        stmt = select(
            OpHistory.biz_id,
            OpHistory.op_id,
            OpHistory.op_type,
            creator_row_num,
            updator_row_num,
        ).where(
            OpHistory.biz_type == biz_type,
            OpHistory.biz_id.in_(biz_ids),
            or_(
                OpHistory.op_type == OpType.ADD.value,  # 创建
                OpHistory.op_type == OpType.UPDATE.value,  # 修改
            ),
        )
        sub_q = stmt.subquery()
        # 只保留每组最早的创建和最新的修改
        outer_stmt = select(
            sub_q.c.biz_id,
            sub_q.c.op_id,
            sub_q.c.op_type,
            sub_q.c.creator_rn,
            sub_q.c.updator_rn,
        ).where(
            or_(
                (sub_q.c.op_type == OpType.ADD.value) & (sub_q.c.creator_rn == 1),
                (sub_q.c.op_type == OpType.UPDATE.value) & (sub_q.c.updator_rn == 1),
            )
        )
        result = await get_db().curr.execute(outer_stmt)
        rows = result.fetchall()

        res: Dict[int, OpUser] = {}
        for biz_id, op_id, op_type, creator_rn, updator_rn in rows:
            if biz_id not in res:
                res[biz_id] = OpUser()
            if op_type == OpType.ADD.value:
                res[biz_id].creator_id = op_id
            elif op_type == OpType.UPDATE.value:
                res[biz_id].updator_id = op_id
        return res

    @classmethod
    async def get_op_ids(
        cls, biz_type: str, biz_ids: List[int]
    ) -> Dict[int, List[int]]:
        if not biz_ids:
            return {}

        result = await get_db().curr.execute(
            select(OpHistory.biz_id, OpHistory.op_id)
            .where(
                OpHistory.biz_type == biz_type,
                OpHistory.biz_id.in_(biz_ids),
            )
            .order_by(OpHistory.biz_id, asc(OpHistory.op_time), asc(OpHistory.id))
        )
        rows = result.fetchall()
        id_map = defaultdict(list)
        for biz_id, op_id in rows:
            id_map[biz_id].append(op_id)
        return id_map


op_history_controller: OpHistoryController = OpHistoryController()


class BizOpInfo:
    def __init__(self, biz_type: str, biz_ids: List[int], userinfo_handler):
        self._biz_type = biz_type
        self._biz_ids = biz_ids
        self._userinfo_handler = userinfo_handler

    async def init(self):
        biz_ops = await op_history_controller.get_creator_and_last_updator_id(
            self._biz_type, self._biz_ids
        )
        user_ids = set()
        for op in biz_ops.values():
            if op.creator_id:
                user_ids.add(op.creator_id)
            if op.updator_id:
                user_ids.add(op.updator_id)
        user_infos = await self._userinfo_handler(user_ids)
        self._biz_ops: Dict[int, OpUser] = biz_ops
        self._user_infos: Dict[int, Any] = user_infos

    def __str__(self):
        return f"biz={self._biz_type} ops={self._biz_ops} users={self._user_infos}"

    def _biz_op_attr(self, biz_id: int, attr: str, op_id_attr: str) -> str:
        if biz_id not in self._biz_ops:
            return ""
        userid = getattr(self._biz_ops[biz_id], attr)
        if userid not in self._user_infos:
            return ""
        return getattr(self._user_infos[userid], op_id_attr)

    def biz_creator_attr(self, biz_id: int, attr: str = "real_name") -> str:
        return self._biz_op_attr(biz_id, "creator_id", attr)

    def biz_updator_attr(self, biz_id: int, attr: str = "real_name") -> str:
        return self._biz_op_attr(biz_id, "updator_id", attr)
