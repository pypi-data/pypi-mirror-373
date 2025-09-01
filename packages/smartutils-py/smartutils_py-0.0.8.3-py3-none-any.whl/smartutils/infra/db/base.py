from typing import TYPE_CHECKING

from smartutils.infra.db.sqlalchemy_cli import AsyncDBCli
from smartutils.infra.resource.manager.manager import CTXResourceManager
from smartutils.init.mixin import LibraryCheckMixin

try:
    from sqlalchemy.ext.asyncio import AsyncSession
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyManager(LibraryCheckMixin, CTXResourceManager[AsyncDBCli]):
    @property
    def curr(self) -> AsyncSession:
        return super().curr[0]
