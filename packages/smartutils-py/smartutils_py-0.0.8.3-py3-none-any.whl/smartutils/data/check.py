import ipaddress
import re
from typing import Optional

from smartutils.data.base import is_num

IPV4_REGEX = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
IPV6_REGEX = re.compile(r"^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$")
DOMAIN_REGEX = re.compile(
    r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*\.[A-Za-z]{2,}$"
)
USERNAME_PATTERN = r"^[a-zA-Z0-9]+$"
MAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

_USERNAME_REGEX = re.compile(USERNAME_PATTERN)
_MAIL_REGEX = re.compile(MAIL_PATTERN)


def check_ip(ip: Optional[str]) -> bool:
    if not isinstance(ip, str):
        return False
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def check_domain(domain: Optional[str]) -> bool:
    if not isinstance(domain, str):
        return False
    return bool(DOMAIN_REGEX.match(domain))


def check_port(port) -> bool:
    if not isinstance(port, int):
        try:
            port = int(port)
        except Exception:
            return False
    return 1 <= port <= 65535


def check_mail(s: Optional[str]) -> bool:
    """检查邮箱格式是否正确

    Args:
        s (str): 邮箱字符串

    Returns:
        bool: 是否正确
    """
    if s is None:
        return False
    return bool(_MAIL_REGEX.fullmatch(s))


def check_phone(s: Optional[str]) -> bool:
    return is_num(s)


def check_username(s: Optional[str]) -> bool:
    """检查用户名格式是否正确

    Args:
        s (str): 用户名字符串

    Returns:
        bool: 是否正确
    """
    if s is None:
        return False
    return bool(_USERNAME_REGEX.fullmatch(s))
