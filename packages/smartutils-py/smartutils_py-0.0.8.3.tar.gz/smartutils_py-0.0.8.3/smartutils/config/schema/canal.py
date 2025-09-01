from typing import List

from pydantic import Field

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.host import HostConf
from smartutils.model.field import StrippedBaseModel

__all__ = ["CanalClientConf", "CanalConf"]


class CanalClientConf(StrippedBaseModel):
    name: str = Field(..., min_length=1, description="客户名")
    client_id: str = Field(..., min_length=1, description="客户ID")
    destination: str = Field(..., min_length=1, description="目前canal实例名")


@ConfFactory.register(ConfKey.CANAL, multi=True, require=False)
class CanalConf(HostConf):
    port: int = 11111
    clients: List[CanalClientConf]
