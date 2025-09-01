from typing import Literal, Optional

from pydantic import Field

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.model.field import StrippedBaseModel

__all__ = ["LoguruConfig"]


@ConfFactory.register(ConfKey.LOGURU, multi=False, require=False)
class LoguruConfig(StrippedBaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    rotation: str = Field(
        default="00:00",
        description="日志轮转条件，如 '10 MB', '1 week', '00:00' 等",
        min_length=1,
    )
    retention: str = Field(
        default="30 days", description="日志保留时长，如 '30 days'", min_length=1
    )
    compression: Literal["zip", "gz", "bz2", "xz", "tar"] = "zip"
    logdir: Optional[str] = Field(None, min_length=1)
    enqueue: bool = True
    stream: bool = False
    backtrace: bool = False
    diagnose: bool = False

    @property
    def stream_kw(self) -> dict:
        return self.model_dump(
            exclude={"rotation", "retention", "compression", "logdir", "stream"}
        )

    @property
    def file_kw(self) -> dict:
        return self.model_dump(exclude={"logdir", "stream"})
