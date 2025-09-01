from typing import List, Optional

from pydantic import Field

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.host import HostConf
from smartutils.config.schema.pool import PoolConf
from smartutils.model.field import StrippedBaseModel

__all__ = ["MongoConf"]


class MongoHostConf(HostConf):
    port: int = 27017


@ConfFactory.register(ConfKey.MONGO, multi=True, require=False)
class MongoConf(StrippedBaseModel, PoolConf):
    hosts: List[MongoHostConf] = Field(..., min_length=1, description="多副本配置")

    user: str = Field(..., min_length=1, description="用户名")
    passwd: str = Field(..., min_length=1, description="密码")
    db: str = Field(..., min_length=1, description="库")

    connect: bool = Field(False, description="是否立即连接服务器")

    replica_set: str = Field("rs0", description="副本集名称（如为副本集时填写）")

    # 统一单位：秒
    connect_timeout: Optional[int] = Field(
        None, gt=0, description="控制连接服务器握手等待的最长时间，默认20秒"
    )
    execute_timeout: Optional[int] = Field(
        None,
        gt=0,
        description="等待 MongoDB 服务器响应的最大超时时间。客户端已连上MongoDB，执行查询/写入过程中单次socket通讯响应的最长等待",
    )

    @property
    def url(self) -> str:
        hosts_str = ",".join([f"{host.host}:{host.port}" for host in self.hosts])
        params = []
        if self.replica_set:
            params.append(f"replicaSet={self.replica_set}")
        params.append("authSource=admin")
        params_str = "&".join(params)
        return f"mongodb://{self.user}:{self.passwd}@{hosts_str}/{self.db}?{params_str}"

    @property
    def kw(self) -> dict:
        connect_timeout_ms = (
            None if not self.connect_timeout else self.connect_timeout * 1000
        )
        execute_timeout_ms = (
            None if not self.execute_timeout else self.execute_timeout * 1000
        )
        params = {
            "maxPoolSize": self.max_pool_size(),
            "minPoolSize": self.min_pool_size(),
            "connectTimeoutMS": connect_timeout_ms,
            "socketTimeoutMS": execute_timeout_ms,
            "serverSelectionTimeoutMS": connect_timeout_ms,
            "waitQueueTimeoutMS": self.pool_timeout * 1000,
            "maxIdleTimeMS": self.pool_recycle * 1000,
            # "maxLifeTimeMS": self.pool_recycle * 1000,
        }
        return params
