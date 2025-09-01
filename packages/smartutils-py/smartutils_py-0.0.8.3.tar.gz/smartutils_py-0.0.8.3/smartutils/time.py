from datetime import datetime, timedelta
from time import time
from typing import Optional, Tuple, Union
from zoneinfo import ZoneInfo

__all__ = [
    "format_time",
    "format_timestamp",
    "get_now",
    "get_now_str",
    "today",
    "yesterday",
    "tomorrow",
    "get_now_stamp",
    "get_now_stamp_float",
    "get_now_stamp_str",
    "get_stamp_after",
    "get_stamp_before",
    "get_pass_time",
    "get_remain_time",
    "parse_time_str",
    "get_timestamp",
    "week_day",
    "week_day_str",
    "today_remain_sec",
]

_DefaultFormat = "%Y-%m-%d %H:%M:%S"
_DefaultTZ = ZoneInfo("Asia/Shanghai")


def format_time(t: datetime, f: str = _DefaultFormat, tz: ZoneInfo = _DefaultTZ) -> str:
    if t.tzinfo is None:
        t = t.replace(tzinfo=tz)
    else:
        t = t.astimezone(tz)
    return t.strftime(f)


def format_timestamp(timestamp: int, tz: ZoneInfo = _DefaultTZ) -> str:
    dt = datetime.fromtimestamp(timestamp, tz)
    return format_time(dt, tz=tz)


def get_now(tz: ZoneInfo = _DefaultTZ):
    return datetime.now(tz)


def get_now_str(tz: ZoneInfo = _DefaultTZ) -> str:
    return format_time(get_now(tz), tz=tz)


def today(tz: ZoneInfo = _DefaultTZ) -> str:
    return format_time(get_now(tz), "%Y-%m-%d", tz=tz)


def yesterday(tz: ZoneInfo = _DefaultTZ) -> str:
    return format_time(get_now(tz) - timedelta(days=1), "%Y-%m-%d", tz=tz)


def tomorrow(tz: ZoneInfo = _DefaultTZ) -> str:
    return format_time(get_now(tz) + timedelta(days=1), "%Y-%m-%d", tz=tz)


def get_now_stamp() -> int:
    """
    获取当前时间戳
    :return:
    """
    return int(get_now_stamp_float())


def get_now_stamp_float() -> float:
    return time()


def get_now_stamp_str() -> str:
    return str(get_now_stamp_float())


def get_stamp_after(
    stamp: Optional[float] = None,
    day: Union[int, float] = 0,
    hour: Union[int, float] = 0,
    minute: Union[int, float] = 0,
    second: Union[int, float] = 0,
) -> float:
    """
    获取一段时间后的时间戳
    :param stamp:
    :param day:
    :param hour:
    :param minute:
    :param second:
    :return:
    """
    if stamp is None:
        stamp = get_now_stamp_float()
    if day:
        hour += day * 24
    if hour:
        minute += hour * 60
    if minute:
        second += minute * 60
    return stamp + second


def get_stamp_before(
    stamp: float = 0, day: int = 0, hour: int = 0, minute: int = 0, second: int = 0
) -> float:
    if not stamp:
        stamp = get_now_stamp_float()
    if day:
        hour -= day * 24
    if hour:
        minute -= hour * 60
    if minute:
        second -= minute * 60
    return stamp - second


def get_pass_time(early: datetime, latest: datetime) -> Tuple[int, int, int, int]:
    """
    获取已经过去了多少天、时、分
    Args:
        early:
        latest:

    Returns:

    """
    d = latest - early
    return d.days, d.seconds // 3600, (d.seconds // 60) % 60, d.seconds % 3600 % 60


def get_remain_time(
    early: datetime, latest: datetime, day: int, hour: int, minute: int, second: int
) -> Tuple[int, int, int, int]:
    """

    Args:
        early: 记录生成的时间点
        latest: 最新的时间点
        day: 记录的天数
        hour: 记录的小时数
        minute: 记录的分钟数
        second: 记录的秒数

    Returns: 距离记录的截止时间，还有多少天、时、分
    """
    deadline = early + timedelta(days=day, hours=hour, minutes=minute, seconds=second)
    if deadline <= latest:
        return 0, 0, 0, 0
    return get_pass_time(latest, deadline)


def parse_time_str(
    time_str: str, str_format: str = _DefaultFormat, tz: ZoneInfo = _DefaultTZ
) -> datetime:
    dt = datetime.strptime(time_str, str_format)
    return dt.replace(tzinfo=tz)


def get_timestamp(t: datetime) -> float:
    return t.timestamp()


def week_day(date=None, tz: ZoneInfo = _DefaultTZ):
    if date is None:
        date = get_now(tz)
    elif date.tzinfo is None:
        date = date.replace(tzinfo=tz)
    else:
        date = date.astimezone(tz)
    return date.weekday()


def week_day_str(date=None, tz: ZoneInfo = _DefaultTZ):
    if date is None:
        date = get_now(tz)
    elif date.tzinfo is None:
        date = date.replace(tzinfo=tz)
    else:
        date = date.astimezone(tz)
    return date.strftime("%A")


def today_remain_sec(tz: ZoneInfo = _DefaultTZ) -> int:
    now = get_now(tz)
    end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=tz)
    delta = end_of_day - now
    return int(delta.total_seconds())


def get_now_hour(tz: ZoneInfo = _DefaultTZ) -> int:
    now = get_now(tz)
    return now.hour
