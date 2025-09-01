from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator, Optional, Tuple

from smartutils.config.schema.mongo import MongoConf
from smartutils.infra.resource.abstract import AbstractAsyncResource
from smartutils.init.mixin import LibraryCheckMixin
from smartutils.log import logger

try:
    from motor.motor_asyncio import (
        AsyncIOMotorClient,
        AsyncIOMotorClientSession,
        AsyncIOMotorDatabase,
    )
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    from motor.motor_asyncio import (
        AsyncIOMotorClient,
        AsyncIOMotorClientSession,
        AsyncIOMotorDatabase,
    )

__all__ = ["AsyncMongoCli"]


class AsyncMongoCli(LibraryCheckMixin, AbstractAsyncResource):
    def __init__(self, conf: MongoConf, name: str):
        self.check(conf=conf, libs=["motor"])

        self._key = name
        self.conf = conf
        self._client: AsyncIOMotorClient = AsyncIOMotorClient(conf.url, **conf.kw)
        self._db: AsyncIOMotorDatabase = self._client[self.conf.db]

    async def ping(self) -> bool:
        try:
            await self._client.admin.command("ping")
            return True
        except Exception:
            logger.exception("{name} MongoDB ping failed", name=self.name)
            return False

    async def close(self):
        self._client.close()

    @asynccontextmanager
    async def db(
        self, use_transaction: bool = False
    ) -> AsyncGenerator[
        Tuple[AsyncIOMotorDatabase, Optional[AsyncIOMotorClientSession]], None
    ]:
        if use_transaction:
            async with await self._client.start_session() as transaction:
                transaction.start_transaction()
                yield self._db, transaction
        else:
            yield self._db, None

    # @property
    # def client(self):
    #     return self._client


async def db_commit(
    session: Tuple[AsyncIOMotorDatabase, Optional[AsyncIOMotorClientSession]],
):
    # if _write_in_session(session):
    if session[1]:
        await session[1].commit_transaction()
    logger.debug("auto commit")


async def db_rollback(
    session: Tuple[AsyncIOMotorDatabase, Optional[AsyncIOMotorClientSession]],
):
    # if _write_in_session(session):
    if session[1]:
        await session[1].abort_transaction()
    logger.debug("auto rollback")
