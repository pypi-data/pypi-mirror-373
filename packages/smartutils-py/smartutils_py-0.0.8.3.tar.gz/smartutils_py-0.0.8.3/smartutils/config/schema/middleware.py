from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from smartutils.config.const import ConfKey
from smartutils.config.factory import ConfFactory


class MiddlewarePluginKey(str, Enum):
    ME = "me"
    PERMISSION = "permission"
    EXCEPTION = "exception"
    HEADER = "header"
    LOG = "log"
    APIKEY = "apikey"
    ECHO = "echo"

    FOR_TEST = "for_test"


class PluginDependAuthConf(BaseModel):
    access_name: str = "access_token"  # 访问令牌name
    local: bool = False  # 是否本地模式，如果为True，则本地逻辑
    client_key: str = "auth"  # 使用配置中client.指向的Client


class PluginApiKeyConf(BaseModel):
    keys: List[str] = []  # 允许访问的key
    header_key: str = "X-API-Key"  # header获取key
    secret: str = ""  # 密钥, 不为空则开启签名模式验证
    header_signature: str = "X-API-Signature"  # header获取签名
    header_timestamp: str = "X-API-Timestamp"  # header获取时间戳


class MiddlewarePluginSetting(BaseModel):
    me: PluginDependAuthConf = Field(
        default_factory=lambda: PluginDependAuthConf(), description="me插件配置"
    )
    permission: PluginDependAuthConf = Field(
        default_factory=lambda: PluginDependAuthConf(), description="permission插件配置"
    )
    apikey: PluginApiKeyConf = Field(
        default_factory=lambda: PluginApiKeyConf(), description="api_key插件配置"
    )


@ConfFactory.register(ConfKey.MIDDLEWARE, multi=False, require=False)
class MiddlewareConf(BaseModel):
    routes: Optional[Dict[str, List[MiddlewarePluginKey]]] = Field(
        None, description="按路由分类的中间件组,app表示全局中间件"
    )
    setting: Optional[MiddlewarePluginSetting] = Field(None, description="中间件配置")

    @property
    def safe_setting(self) -> MiddlewarePluginSetting:
        return self.setting or MiddlewarePluginSetting()
