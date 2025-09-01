from pydantic import Field

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.model.field import StrippedBaseModel

__all__ = ["TokenConf"]


@ConfFactory.register(ConfKey.TOKEN, multi=False, require=False)
class TokenConf(StrippedBaseModel):
    access_secret: str = Field(..., min_length=1)
    access_exp_min: int = Field(..., gt=0)
    refresh_secret: str = Field(..., min_length=1)
    refresh_exp_day: int = Field(..., gt=0)
