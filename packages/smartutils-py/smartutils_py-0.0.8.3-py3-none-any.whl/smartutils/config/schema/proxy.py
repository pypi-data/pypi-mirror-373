from pydantic import BaseModel

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory


@ConfFactory.register(ConfKey.PROXY, multi=False, require=False)
class ProxyConf(BaseModel):
    url: str
