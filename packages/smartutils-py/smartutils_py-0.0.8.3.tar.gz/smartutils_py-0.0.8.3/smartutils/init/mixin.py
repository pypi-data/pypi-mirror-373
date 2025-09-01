from typing import List, Optional

from smartutils.call import installed
from smartutils.design import MyBase
from smartutils.error.sys import LibraryUsageError


class LibraryCheckMixin(MyBase):
    def check(
        self, *, libs: Optional[List[str]] = None, conf=None, require_conf: bool = True
    ):
        if libs:
            not_loaded = [lib for lib in libs if not installed(lib)]
            if not_loaded:
                libs_str = ", ".join(not_loaded)
                raise LibraryUsageError(
                    f"{self.name} depend on {libs_str}, install first!"
                )

        if require_conf:
            if conf is None:
                raise LibraryUsageError(
                    f"{self.name} require conf, init by infra normally."
                )
