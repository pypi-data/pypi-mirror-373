import html
import re
from typing import Optional, Dict
from urllib.parse import urlparse, urlencode, urljoin, unquote, urlunparse, ParseResult


def _parse_url_segments(url: str) -> ParseResult:
    """
    解析URL为各组成部分。

    Args:
        url (str): 要解析的URL。
    Returns:
        tuple: (scheme, netloc, path, params, query, fragment)
    """
    return urlparse(url)


def url_path(url: str) -> str:
    """获取URL的路径部分（/path/to/file）"""
    return _parse_url_segments(url).path


def replace_url_host(url: str, host: str) -> str:
    """
    替换URL中的主机部分（netloc）。

    Args:
        url (str): 原始URL。
        host (str): 新主机名（如 example.com:8080）。
    Returns:
        str: 替换主机后的新URL。
    """
    seg = _parse_url_segments(url)
    return urlunparse((seg.scheme, host, seg.path, seg.params, seg.query, seg.fragment))


def is_valid_url(url: str) -> bool:
    """
    判断URL是否有scheme和host部分（基本合法）。

    Args:
        url (str): 待校验URL。
    Returns:
        bool: 合法返回True，否则False。
    """
    if not isinstance(url, str):
        return False
    seg = _parse_url_segments(url)
    return bool(seg.scheme and seg.netloc)


def has_url_path(url: str) -> bool:
    """
    判断URL是否有路径部分。

    Args:
        url (str): 待校验URL。
    Returns:
        bool: 有路径返回True，否则False。
    """
    return _parse_url_segments(url).path != ""


def url_host(url: str) -> str:
    """
    获取URL的主机（含协议）。

    Args:
        url (str): 输入URL。
    Returns:
        str: 形如 http(s)://domain 的字符串。
    """
    seg = _parse_url_segments(url)
    return f"{seg.scheme}://{seg.netloc}" if seg.scheme and seg.netloc else ""


def is_same_host(u1: str, u2: str) -> bool:
    """
    判断两个URL主机部分是否一致。
    """
    return (
        is_valid_url(u1)
        and is_valid_url(u2)
        and _parse_url_segments(u1).netloc == _parse_url_segments(u2).netloc
    )


def is_same_url(u1: str, u2: str) -> bool:
    """
    判断两个URL完全等价（解码后各部分完全一致）。
    """
    u1_dec = url_decode(u1)
    u2_dec = url_decode(u2)
    if not is_valid_url(u1_dec) or not is_valid_url(u2_dec):
        return False
    seg1 = _parse_url_segments(u1_dec)
    seg2 = _parse_url_segments(u2_dec)
    return (
        seg1.scheme,
        seg1.netloc,
        seg1.path,
        seg1.params,
        seg1.query,
        seg1.fragment,
    ) == (seg2.scheme, seg2.netloc, seg2.path, seg2.params, seg2.query, seg2.fragment)


def is_url_missing_host(url: str) -> bool:
    """
    判断URL是否缺少 scheme 和 host（如只有路径）。
    """
    seg = _parse_url_segments(url)
    return not seg.scheme and not seg.netloc


def resolve_relative_url(base_url: str, href: str) -> str:
    """
    用urljoin将href相对路径补全为完整URL。
    """
    return urljoin(url_host(base_url), href)


def html_encode(s: str) -> str:
    """HTML转义"""
    return html.escape(s)


def html_decode(s: str) -> str:
    """HTML反转义"""
    return html.unescape(s)


def url_decode(s: str) -> str:
    """URL解码"""
    return unquote(s)


def url_filename(url: str) -> str:
    """
    获取URL路径的最后一段（文件名）。
    """
    path = url_path(url)
    return path.rstrip("/").rsplit("/", 1)[-1] if path else ""


_UrlRegex = re.compile(r"https?://(?:[-\w.]|%[\da-fA-F]{2})+")


def find_url_in_text(s: str) -> Optional[str]:
    """
    从文本中提取第一个 http(s) URL，找不到返回None。
    """
    match = _UrlRegex.search(s)
    return match.group(0) if match else None


def url_last_segment(url: str) -> str:
    """
    获取URL路径的最后一段。
    """
    return url_filename(url)


def dict_to_query_params(data: Dict) -> str:
    """
    字典转URL参数字符串。
    """
    return urlencode(data)
