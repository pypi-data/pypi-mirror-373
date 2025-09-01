from smartutils.ID.const import IDGenType
from smartutils.ID.init import IDGen

__all__ = ["IDGen", "IDGenType"]

from smartutils.ID import gens
from smartutils.call import register_package

register_package(gens)
