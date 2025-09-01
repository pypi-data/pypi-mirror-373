from typing import Dict, Optional, Tuple, cast

from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.config.schema.middleware import PluginDependAuthConf
from smartutils.design import MyBase
from smartutils.error.sys import LibraryUsageError
from smartutils.infra.client.http import HttpClient
from smartutils.infra.client.manager import ClientManager


class AuthBase(MyBase):
    def __init__(self, *, plugin_conf: PluginDependAuthConf, **kwargs):
        super().__init__(**kwargs)

        self._plugin_conf = plugin_conf

        try:
            if not self._plugin_conf.local:
                self._client = cast(
                    HttpClient,
                    ClientManager().client(plugin_conf.client_key),
                )
        except LibraryUsageError:
            raise LibraryUsageError(
                f"{self.name} requires auth below client in config.yaml."
            )

    def access_token(self, req: RequestAdapter) -> Tuple[str, str]:
        token = req.get_cookie(self._plugin_conf.access_name)
        return token, "" if token else "request no cookies."

    def mk_cookies(self, req: RequestAdapter) -> Tuple[Optional[Dict], str]:
        token, msg = self.access_token(req)
        if msg:
            return None, msg
        return {self._plugin_conf.access_name: token}, ""
