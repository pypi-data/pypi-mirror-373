from typing import Dict, Tuple, Type, Union

from pydantic import ValidationError

from smartutils.config.const import BaseModelT, ConfKey
from smartutils.design import BaseFactory, MyBase
from smartutils.error.factory import ExcDetailFactory
from smartutils.error.sys import ConfigError
from smartutils.log import logger

__all__ = ["ConfFactory"]


class ConfFactory(MyBase, BaseFactory[ConfKey, Tuple[Type, bool, bool]]):
    @classmethod
    def register(cls, name: ConfKey, multi: bool = False, require: bool = False):  # type: ignore
        def decorator(conf_cls: Type):
            super(ConfFactory, cls).register(name, only_register_once=False)(
                (conf_cls, multi, require)
            )
            return conf_cls

        return decorator

    @classmethod
    def _init_conf_cls(cls, name, key, conf_cls, conf):
        try:
            return conf_cls(**conf)
        except ValidationError as e:
            raise ConfigError(
                f"{cls.name} invalid {name}-{key} in config.yml: {ExcDetailFactory.get(e)}"
            )

    @classmethod
    def create(
        cls, name: ConfKey, conf: Dict
    ) -> Union[BaseModelT, dict[str, BaseModelT], None]:
        info = cls.get(name)

        conf_cls, multi, require = info
        if not conf:
            if require:
                raise ConfigError(f"{cls.name} require {name} in config.yml")
            # logger.debug(
            #     "{cls_name} no {name} in config.yml, ignore.",
            #     cls_name=cls.name,
            #     name=name,
            # )
            return None

        logger.info("{cls_name} {name} created.", cls_name=cls.name, name=name)

        if multi:
            # if ConfKey.GROUP_DEFAULT not in conf:
            #     raise ConfigError(
            #         f"ConfFactory no {ConfKey.GROUP_DEFAULT} below {name}"
            #     )

            return {
                key: cls._init_conf_cls(name, key, conf_cls, _conf)
                for key, _conf in conf.items()
            }
        else:
            return cls._init_conf_cls(name, "", conf_cls, conf)
