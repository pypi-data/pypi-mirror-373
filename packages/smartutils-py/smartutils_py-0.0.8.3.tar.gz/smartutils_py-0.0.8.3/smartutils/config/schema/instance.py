from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.time import get_timestamp

__all__ = ["InstanceConf"]


@ConfFactory.register(ConfKey.INSTANCE, multi=False, require=False)
class InstanceConf(BaseModel):
    id: int = Field(..., description="保证每实例有唯一ID", ge=0)
    release_time: datetime = Field(..., description="例如：2025-05-07 10:00:00+08:00")

    @field_validator("release_time", mode="after")
    def must_be_aware(cls, v):
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            raise ValueError(
                "release_time must be an aware datetime (must contain timezone)"
            )
        return v

    @property
    def release_timestamp_ms(self) -> int:
        return int(get_timestamp(self.release_time)) * 1000

    @property
    def kw(self) -> dict:
        return {"instance": self.id, "epoch": self.release_timestamp_ms}
