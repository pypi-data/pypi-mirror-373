from typing import Any, Callable

from smartutils.config import Config, ConfKey
from smartutils.design import BaseFactory, MyBase
from smartutils.log import logger

__all__ = ["InitByConfFactory"]


class InitByConfFactory(MyBase, BaseFactory[ConfKey, Callable[[Any], Any]]):
    # @classmethod
    # def register(cls, key: ConfKey, need_conf: bool = True, **kwargs):  # type: ignore
    #     def decorator(func: Callable[[Any], Any]):
    #         super(InitByConfFactory, cls).register(key, **kwargs)((func, need_conf))
    #         return func

    #     return decorator

    @classmethod
    def init(cls, config: Config):
        # for comp_key, info in cls.all():
        #     init_func, need_conf = info
        for comp_key, init_func in cls.all():
            conf = config.get(comp_key)
            # if need_conf and not conf:
            if not conf:
                logger.debug(
                    "{name} init by conf no {comp_key}, ignore.",
                    name=cls.name,
                    comp_key=comp_key,
                )
                continue

            logger.debug(
                "{name} init by conf initializing {comp_key} ...",
                name=cls.name,
                comp_key=comp_key,
            )

            init_func(conf)

            logger.info(
                "{name} init by conf {comp_key} inited.",
                name=cls.name,
                comp_key=comp_key,
            )
