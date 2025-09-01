from pydantic import Field, field_validator

from smartutils.data.check import check_domain, check_ip, check_port
from smartutils.model.field import StrippedBaseModel

__all__ = ["HostConf"]


class HostConf(StrippedBaseModel):
    host: str = Field(..., min_length=1, description="ip/域名")
    port: int

    # 考虑直接使用容器名访问
    # @field_validator("host")
    # @classmethod
    # def check_host(cls, v):
    #     if not v or not (check_ip(v) or check_domain(v) or v == "localhost"):
    #         raise ValueError("host不能为空，且必须是有效的IP地址、域名或localhost")
    #     return v

    @field_validator("port")
    @classmethod
    def check_port(cls, v):
        if not check_port(v):
            raise ValueError("port必须在1-65535之间")
        return v

    @property
    def the_url(self) -> str:
        return f"{self.host}:{self.port}"
