from sqlalchemy import Integer, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampedMixin:
    __table__ = ""

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="ID"
    )
    created_at: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=func.unix_timestamp(),
        comment="创建时间",
    )
    updated_at: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=func.unix_timestamp(),
        onupdate=func.unix_timestamp(),
        comment="最后更新时间",
    )
