from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

try:
    from sqlalchemy import JSON, Column, Integer, String, func
    from sqlalchemy.orm import declarative_base
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy import JSON, Column, Integer, String, func
    from sqlalchemy.orm import declarative_base


Base = declarative_base()


class OpType(int, Enum):
    ADD = 1
    DEL = 2
    UPDATE = 3


class OpHistory(Base):
    """
    CREATE TABLE `op_history` (
        `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        `biz_type` VARCHAR(64) NOT NULL COMMENT '业务类型',
        `biz_id` INT UNSIGNED NOT NULL COMMENT '业务主键',
        `op_type` VARCHAR(32) NOT NULL COMMENT '操作类型 1增 2删 3改',
        `op_id` INT UNSIGNED NOT NULL COMMENT '操作人ID',
        `op_time` INT UNSIGNED NOT NULL DEFAULT (UNIX_TIMESTAMP()) COMMENT '操作时间',
        `before_data` JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT '操作前数据',
        `after_data` JSON NOT NULL DEFAULT (JSON_OBJECT()) COMMENT '操作后数据'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    __tablename__ = "op_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    biz_type = Column(String(64), nullable=False, comment="业务类型")
    biz_id = Column(Integer, nullable=False, index=True, comment="业务主键")
    op_type = Column(Integer, nullable=False, comment="操作类型 1增 2删 3改")
    op_id = Column(Integer, nullable=False, index=True, comment="操作人ID")
    op_time = Column(
        Integer,
        nullable=False,
        index=True,
        server_default=func.unix_timestamp(),
        comment="操作时间",
    )
    before_data = Column(JSON, nullable=False, default="{}", comment="操作后数据")
    after_data = Column(JSON, nullable=False, default="{}", comment="操作后数据")
    remark = Column(String(32), nullable=False, default="", comment="备注")
