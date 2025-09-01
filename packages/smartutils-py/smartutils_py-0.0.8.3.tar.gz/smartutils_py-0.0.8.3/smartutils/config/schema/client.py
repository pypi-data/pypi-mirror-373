from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.breaker import BreakerConf


class ClientType(str, Enum):
    HTTP = "http"
    GRPC = "grpc"


class ApiConf(BaseModel):
    path: str
    method: str
    mock: Optional[Dict] = None
    timeout: Optional[int | float] = None


@ConfFactory.register(ConfKey.CLIENT, multi=True, require=False)
class ClientConf(BreakerConf):
    type: ClientType
    endpoint: str
    timeout: int | float = 10
    tls: bool = False
    verify_tls: bool = True
    apis: Optional[Dict[str, ApiConf]] = None
