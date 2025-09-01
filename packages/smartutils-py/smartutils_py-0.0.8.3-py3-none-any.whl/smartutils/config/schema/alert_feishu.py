from typing import List

from pydantic import BaseModel

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory


@ConfFactory.register(ConfKey.ALERT_FEISHU, multi=False, require=False)
class AlertFeishuConf(BaseModel):
    enable: bool = True
    webhooks: List[str]
