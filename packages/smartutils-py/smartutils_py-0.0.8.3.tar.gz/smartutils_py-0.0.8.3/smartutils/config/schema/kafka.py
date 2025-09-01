from typing import List, Literal

from pydantic import Field

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.host import HostConf
from smartutils.model.field import StrippedBaseModel

__all__ = ["KafkaConf"]


@ConfFactory.register(ConfKey.KAFKA, multi=True, require=False)
class KafkaConf(StrippedBaseModel):
    bootstrap_servers: List[HostConf] = Field(..., min_length=1)
    client_id: str = Field(..., min_length=1)
    acks: Literal["all", 1, 0] = "all"
    compression_type: Literal["zstd", "snappy", None] = None
    max_batch_size: int = Field(16384, gt=0)
    linger_ms: int = Field(0, ge=0)
    request_timeout_ms: int = Field(40000, gt=0)
    retry_backoff_ms: int = Field(100, gt=0)

    @property
    def urls(self) -> List[str]:
        return [item.the_url for item in self.bootstrap_servers]

    @property
    def kw(self) -> dict:
        params = self.model_dump(exclude={"bootstrap_servers"})
        return params
