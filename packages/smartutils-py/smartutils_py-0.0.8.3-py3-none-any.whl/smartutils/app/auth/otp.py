import base64
from io import BytesIO
from typing import TYPE_CHECKING, Tuple

from smartutils.design import SingletonMeta
from smartutils.init.mixin import LibraryCheckMixin

try:
    import pyotp
    import qrcode
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    import pyotp
    import qrcode

__all__ = ["OtpHelper"]


class OtpHelper(LibraryCheckMixin, metaclass=SingletonMeta):
    def __init__(self):
        self.check(require_conf=False, libs=["pyotp", "qrcode"])
        super().__init__()

    @staticmethod
    def generate_qr(username: str) -> Tuple[str, str]:
        otp_secret = pyotp.random_base32()
        totp = pyotp.TOTP(otp_secret)

        otp_auth_url = totp.provisioning_uri(name=username, issuer_name="auth")

        img = qrcode.make(otp_auth_url)
        buf = BytesIO()
        img.save(buf)
        img_str = base64.b64encode(buf.getvalue()).decode("utf-8")
        return otp_secret, img_str

    @staticmethod
    def verify_totp(otp_secret: str, user_totp: str) -> bool:
        totp = pyotp.TOTP(otp_secret)
        return totp.verify(user_totp)
