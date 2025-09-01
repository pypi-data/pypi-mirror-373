from pydantic import Field

from smartutils.config.schema.host import HostConf
from smartutils.config.schema.pool import PoolConf

__all__ = ["DBConf"]


class DBConf(HostConf, PoolConf):
    user: str = Field(..., min_length=1, description="用户名")
    passwd: str = Field(..., min_length=1, description="密码")
    db: str = Field(..., min_length=1, description="库")

    echo: bool = False
    echo_pool: bool = False

    @property
    def kw(self) -> dict:
        params = self.model_dump(exclude={"user", "passwd", "db", "host", "port"})
        return params
