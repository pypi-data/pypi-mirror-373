from typing import Callable, Type

from smartutils.app.adapter.middleware.abstract import AbstractMiddlewarePlugin
from smartutils.config.schema.middleware import MiddlewarePluginKey
from smartutils.design import BaseFactory

__all__ = ["MiddlewarePluginFactory"]


class MiddlewarePluginFactory(
    BaseFactory[MiddlewarePluginKey, Type[AbstractMiddlewarePlugin]]
):
    @classmethod
    def register(  # type: ignore
        cls, key: MiddlewarePluginKey, **kwargs
    ) -> Callable[[type[AbstractMiddlewarePlugin]], type[AbstractMiddlewarePlugin]]:
        def decorator(plugin_cls):
            plugin_cls.key = key
            return super(MiddlewarePluginFactory, cls).register(key, **kwargs)(
                plugin_cls
            )

        return decorator
