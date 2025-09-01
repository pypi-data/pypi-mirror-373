from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Optional, Tuple, Union

from smartutils.config.schema.mysql import MySQLConf
from smartutils.config.schema.postgresql import PostgreSQLConf
from smartutils.infra.resource.abstract import AbstractAsyncResource
from smartutils.init.mixin import LibraryCheckMixin
from smartutils.log import logger

try:
    from sqlalchemy.ext.asyncio import (
        AsyncEngine,
        AsyncSession,
        AsyncSessionTransaction,
        async_sessionmaker,
        create_async_engine,
    )
    from sqlalchemy.sql import text
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.ext.asyncio import (
        AsyncEngine,
        AsyncSession,
        AsyncSessionTransaction,
        async_sessionmaker,
        create_async_engine,
    )
    from sqlalchemy.sql import text

__all__ = ["AsyncDBCli", "db_commit", "db_rollback"]


# _FLUSHED = "smartutils_flushed"


# class MarkedAsyncSession(AsyncSession):
#     async def flush(self, *args, **kwargs):
#         result = await super().flush(*args, **kwargs)
#         self.info[_FLUSHED] = True
#         return result


class AsyncDBCli(LibraryCheckMixin, AbstractAsyncResource):
    def __init__(self, conf: Union[MySQLConf, PostgreSQLConf], name: str):
        self.check(conf=conf, libs=["sqlalchemy"])

        self._key = name
        kw = conf.kw
        kw["pool_reset_on_return"] = "rollback"
        kw["pool_pre_ping"] = True
        kw["future"] = True

        self._engine: AsyncEngine = create_async_engine(conf.url, **kw)
        self._session = async_sessionmaker(
            bind=self._engine,
            # class_=MarkedAsyncSession,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    async def ping(self) -> bool:
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except:  # noqa
            logger.exception("{name} DB ping failed", name=self.name)
            return False

    async def close(self):
        await self._engine.dispose()

    @asynccontextmanager
    async def db(
        self, use_transaction: bool = False
    ) -> AsyncGenerator[Tuple[AsyncSession, Optional[AsyncSessionTransaction]], None]:
        async with self._session() as session:
            if use_transaction:
                trans = await session.begin()
                yield session, trans
            else:
                yield session, None

    @property
    def engine(self):
        return self._engine

    # async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
    #     session = self._session()
    #     try:
    #         yield session
    #     finally:
    #         await session.close()

    async def create_tables(self, bases):
        async with self.engine.begin() as conn:
            for base in bases:
                await conn.run_sync(base.metadata.create_all)


# def _write_in_session(session: AsyncSession):
#     written = bool(session.new) or bool(session.dirty) or bool(session.deleted)
#     flushed = session.info.get(_FLUSHED, False)
#     in_t = hasattr(session, "in_transaction") and session.in_transaction()
#     logger.debug("written={a};flushed={b};in_t={c}", a=written, b=flushed, c=in_t)
#     return written or flushed and in_t


async def db_commit(session: Tuple[AsyncSession, Optional[AsyncSessionTransaction]]):
    # if _write_in_session(session):
    if session[1]:
        await session[1].commit()
    else:
        await session[0].commit()
    logger.debug("auto commit")


async def db_rollback(session: Tuple[AsyncSession, Optional[AsyncSessionTransaction]]):
    # if _write_in_session(session):
    if session[1]:
        await session[1].rollback()
    else:
        await session[0].rollback()
    logger.debug("auto rollback")
