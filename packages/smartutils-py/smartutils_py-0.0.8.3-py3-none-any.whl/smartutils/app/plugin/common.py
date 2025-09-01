import base64
from typing import List, Optional

from smartutils.app.adapter.req.abstract import RequestAdapter
from smartutils.app.const import HeaderKey
from smartutils.design import MyBase
from smartutils.log import logger


class CustomHeader(MyBase):
    @classmethod
    def userid(cls, adapter: RequestAdapter, value: Optional[int] = None) -> int:
        if value is not None:
            adapter.set_header(HeaderKey.X_USER_ID, str(value))
            return 0

        userid = adapter.get_header(HeaderKey.X_USER_ID)
        if not userid:
            return 0
        return int(userid)

    @classmethod
    def username(cls, adapter: RequestAdapter, value: Optional[str] = None) -> str:
        if value is not None:
            adapter.set_header(
                HeaderKey.X_USER_NAME,
                base64.b64encode(value.encode("utf-8")).decode("utf-8"),
            )
            return ""

        username = adapter.get_header(HeaderKey.X_USER_NAME)
        if not username:
            return ""
        return base64.b64decode(username).decode("utf-8")

    @classmethod
    def traceid(cls, adapter: RequestAdapter) -> str:
        return adapter.get_header(HeaderKey.X_TRACE_ID)

    @classmethod
    def permission_user_ids(
        cls,
        adapter: RequestAdapter,
        value: Optional[List[int]] = None,
        set_value: bool = False,
    ) -> Optional[List[int]]:
        if set_value:
            if value:
                adapter.set_header(
                    HeaderKey.X_P_USER_IDS, ",".join([str(i) for i in value])
                )
            return

        ids = adapter.get_header(HeaderKey.X_P_USER_IDS)
        if not ids:
            return None
        if not isinstance(ids, str):
            logger.error(
                "{name} get {ids}, not str, {type}",
                name=cls.name,
                ids=ids,
                type=type(ids),
            )
            return None
        return [int(s) for s in ids.split(",")]
