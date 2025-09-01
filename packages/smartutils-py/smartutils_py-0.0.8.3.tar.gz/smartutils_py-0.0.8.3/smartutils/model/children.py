from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Type

try:
    from sqlalchemy import Column, select
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import aliased
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy import Column, select
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import aliased


async def children_ids(
    session: AsyncSession,
    model: Type,
    pk_field: Column,
    parent_pk_field: Column,
    root_id: Any,
) -> List[int]:
    """
    通用递归查找树结构所有子节点ID。
    不做环检测，太复杂，用数据库超时代替
    :param session: SQLAlchemy AsyncSession
    :param model: ORM模型类
    :param pk_field: 主键字段，如 model.id
    :param parent_pk_field: 父ID字段，如 model.parent_id
    :param root_id: 根节点ID
    :return: 子节点ID列表（不含自身）
    """
    sub_query = (
        select(pk_field)
        .where(parent_pk_field == root_id)
        .cte(name="sub_nodes", recursive=True)
    )
    node_alias = aliased(model)
    sub_query = sub_query.union_all(
        select(node_alias.id).where(node_alias.parent_id == sub_query.c.id)
    )
    result = await session.execute(select(sub_query.c.id))
    return list(result.scalars().all())
