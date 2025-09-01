from __future__ import annotations

from typing import Dict, Optional, Union

from smartutils.config.const import ConfKey
from smartutils.config.schema.client import ClientConf, ClientType
from smartutils.ctx.const import CTXKey
from smartutils.ctx.manager import CTXVarManager
from smartutils.design import singleton
from smartutils.error.sys import ClientError
from smartutils.infra.client.grpc import GrpcClient
from smartutils.infra.client.http import HttpClient
from smartutils.infra.resource.manager.manager import CTXResourceManager
from smartutils.init.factory import InitByConfFactory
from smartutils.init.mixin import LibraryCheckMixin
from smartutils.log import logger

# TODO: 封装返回数据，外部统一操作


@singleton
@CTXVarManager.register(CTXKey.CLIENT)
class ClientManager(
    LibraryCheckMixin, CTXResourceManager[Union[HttpClient, GrpcClient]]
):
    def __init__(self, confs: Optional[Dict[str, ClientConf]] = None):
        self.check(conf=confs)
        assert confs

        resources = {}
        for k, conf in confs.items():
            if conf.type == ClientType.HTTP:
                resources[k] = HttpClient(conf, f"client_http_{k}")
            elif conf.type == ClientType.GRPC:
                resources[k] = GrpcClient(conf, f"client_grpc_{k}")
            else:
                logger.error(f"{self.name} get unexcepted key {k} in config, ignore.")

        super().__init__(resources=resources, ctx_key=CTXKey.CLIENT, error=ClientError)

    @property
    def curr(self) -> Union[HttpClient, GrpcClient]:
        return super().curr


@InitByConfFactory.register(ConfKey.CLIENT)
def _(conf):
    ClientManager(conf)
