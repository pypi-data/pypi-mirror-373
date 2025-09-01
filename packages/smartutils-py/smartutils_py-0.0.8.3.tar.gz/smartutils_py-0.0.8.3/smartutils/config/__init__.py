from smartutils.config._config import Config
from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory
from smartutils.config.schema.project import ProjectConf

__all__ = ["Config", "ConfFactory", "ConfKey", "ProjectConf"]

from smartutils.call import register_package
from smartutils.config import schema

register_package(schema)
