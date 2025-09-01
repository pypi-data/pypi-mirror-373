from typing import TYPE_CHECKING, Tuple

from smartutils.design import SingletonMeta
from smartutils.init.mixin import LibraryCheckMixin

try:
    import bcrypt
except ImportError:
    ...

if TYPE_CHECKING:  # pragma: no cover
    import bcrypt

__all__ = ["PasswordHelper"]


class PasswordHelper(LibraryCheckMixin, metaclass=SingletonMeta):
    def __init__(self):
        self.check(require_conf=False, libs=["bcrypt"])
        super().__init__()

    @staticmethod
    def hash_password(plain_password: str) -> Tuple[str, str]:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return salt.decode("utf-8"), hashed_password.decode("utf-8")

    @staticmethod
    def check_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
