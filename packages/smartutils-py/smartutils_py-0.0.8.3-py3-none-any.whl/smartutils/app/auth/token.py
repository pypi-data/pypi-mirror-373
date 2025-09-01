from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Tuple, TypeAlias

from smartutils.config import ConfKey
from smartutils.config.schema.token import TokenConf
from smartutils.design import SingletonMeta
from smartutils.init.factory import InitByConfFactory
from smartutils.init.mixin import LibraryCheckMixin
from smartutils.time import get_stamp_after

try:
    import jwt
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    import jwt

__all__ = ["User", "Token", "TokenHelper"]


@dataclass
class User:
    id: int
    name: str


@dataclass
class Token:
    token: str
    exp: int


AccessToken: TypeAlias = Token
RefreshToken: TypeAlias = Token


class TokenHelper(LibraryCheckMixin, metaclass=SingletonMeta):
    def __init__(self, conf: Optional[TokenConf] = None):
        self.check(conf=conf, libs=["jwt"])
        assert conf

        self._access_secret: str = conf.access_secret
        self._access_exp_sec: int = conf.access_exp_min * 60
        self._refresh_secret: str = conf.refresh_secret
        self._refresh_exp_sec: int = conf.refresh_exp_day * 24 * 60 * 60
        self._userid_key = "userid"
        self._username_key = "username"

    def _generate_token(self, user: User, secret: str, exp_sec: int) -> Token:
        exp_time = int(get_stamp_after(second=exp_sec))

        token = jwt.encode(
            {self._userid_key: user.id, self._username_key: user.name, "exp": exp_time},
            secret,
            algorithm="HS256",
        )
        return Token(token, exp_time)

    @staticmethod
    def _verify_token(token: str, secret: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def token(self, user: User) -> Tuple[AccessToken, RefreshToken]:
        access_t = self._generate_token(user, self._access_secret, self._access_exp_sec)
        refresh_t = self._generate_token(
            user, self._refresh_secret, self._refresh_exp_sec
        )
        return access_t, refresh_t

    def verify_access_token(self, token: str) -> Optional[User]:
        data = self._verify_token(token, self._access_secret)
        if not data:
            return None
        return User(data[self._userid_key], data[self._username_key])

    def refresh(self, refresh_token) -> Optional[Tuple[AccessToken, RefreshToken]]:
        payload = self._verify_token(refresh_token, self._refresh_secret)
        if not payload:
            return None
        user = User(payload["userid"], payload["username"])
        access_t = self._generate_token(user, self._access_secret, self._access_exp_sec)
        # 默认刷新token不延期
        # access_t, refresh_t = self.token(user)
        return access_t, Token(refresh_token, payload["exp"])


@InitByConfFactory.register(ConfKey.TOKEN)
def _(conf):
    TokenHelper(conf)
