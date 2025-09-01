import uuid
from collections import defaultdict
from typing import Dict, List, Optional, OrderedDict, Tuple

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.app.adapter.middleware.factory import (
    AddMiddlewareFactory,
    EndpointMiddlewareFactory,
    RouteMiddlewareFactory,
)
from smartutils.app.const import AppKey, RunEnv
from smartutils.app.plugin.factory import MiddlewarePluginFactory
from smartutils.app.plugin.log import LogPlugin
from smartutils.config.const import ConfKey
from smartutils.config.schema.middleware import MiddlewareConf, MiddlewarePluginKey
from smartutils.design import MyBase, SingletonMeta
from smartutils.error.sys import LibraryUsageError
from smartutils.init.factory import InitByConfFactory
from smartutils.log import logger


class MiddlewareManager(MyBase, metaclass=SingletonMeta):
    ROUTE_APP_KEY = "app"

    def __init__(self, conf: Optional[MiddlewareConf] = None):
        if not conf:
            logger.info("{} no conf, only default init.", self.name)
            conf = MiddlewareConf()

        self._conf: MiddlewareConf = conf
        self._route_ps: Dict[str, List[AbstractMiddlewarePlugin]] = {}
        self._route_inited: bool = False
        self._app_inited: bool = False
        self._default_route_id = f"smartutils:{str(uuid.uuid4())}"

    def _init_route(self) -> None:
        if self._route_inited:
            return

        self._app_key: AppKey = RunEnv.get_app()
        assert self._app_key, f"{self.name} should call RunEnv.set_app() first."

        self._route_inited = True

        routes = self._conf.routes or {}
        routes[self._default_route_id] = [
            MiddlewarePluginKey.LOG,
            MiddlewarePluginKey.EXCEPTION,
        ]

        all_enables = {name for v in routes.values() for name in v}
        plugins = OrderedDict()  # 兼容3.7以下
        for plugin_name, plugin_cls in MiddlewarePluginFactory.all():
            if plugin_name in all_enables:
                plugins[plugin_name] = plugin_cls(conf=self._conf.safe_setting)

        result = defaultdict(list)
        for plugin_name, plugin in plugins.items():
            for key, enables in routes.items():
                if plugin_name not in enables:
                    continue
                logger.debug("{} enable {} for route {}.", self.name, plugin.key, key)
                result[key].append(plugin)
        self._route_ps = result

    def _get_ps(self, route_key: str) -> Tuple[AbstractMiddlewarePlugin, ...]:
        self._init_route()
        if route_key not in self._route_ps:
            raise LibraryUsageError(
                f"{self.name} require {route_key} below middleware.routes in config.yaml."
            )

        return tuple(self._route_ps[route_key])

    # TODO: 其他框架的中间件执行顺序和添加顺序
    def init_app(self, app):
        if self._app_inited:
            raise LibraryUsageError(
                f"{self.name} Cannot init middleware for app key {self._app_key} twice."
            )
        self._app_inited = True

        try:
            ps = self._get_ps(self.ROUTE_APP_KEY)
        except LibraryUsageError:
            logger.debug(
                "{} no {} below middleware.routes in config.yaml, ignore.",
                self.name,
                self.ROUTE_APP_KEY,
            )
            return

        logger.info("{} inited in app.", self.name)
        AddMiddlewareFactory.get(self._app_key)(app, ps)

    def init_route(self, route_key: str):
        ps = self._get_ps(route_key)
        return RouteMiddlewareFactory.get(self._app_key)(ps)

    def init_endpoint(self, route_key: str):
        logger.info("{} inited in endpoint {}.", self.name, route_key)
        ps = self._get_ps(route_key)
        return EndpointMiddlewareFactory.get(self._app_key)(ps)

    def init_default_route(self):
        logger.info("{} init default route.", self.name)
        return RouteMiddlewareFactory.get(self._app_key)(
            self._get_ps(self._default_route_id)
        )


@InitByConfFactory.register(ConfKey.MIDDLEWARE)
def _(conf: MiddlewareConf):
    MiddlewareManager(conf)
