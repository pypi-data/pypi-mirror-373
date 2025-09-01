from typing import Optional

from pydantic import Field

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.host import HostConf

__all__ = ["RedisConf"]


@ConfFactory.register(ConfKey.REDIS, multi=True, require=False)
class RedisConf(HostConf):
    db: int = Field(..., ge=0)
    port: int = 6379
    max_connections: int = Field(10, alias="pool_size")
    socket_connect_timeout: Optional[int] = Field(None, alias="connect_timeout", gt=0)
    socket_timeout: Optional[int] = Field(None, gt=0)
    password: Optional[str] = Field(None, alias="passwd", min_length=1)
    health_check_interval: int = Field(30, alias="health_check_sec", gt=0)
    retry_on_timeout: bool = True

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}"

    @property
    def kw(self) -> dict:
        params = self.model_dump(exclude={"host", "port"})
        return params
