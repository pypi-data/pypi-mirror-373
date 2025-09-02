from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from datetime import tzinfo
from functools import partial
from typing import NotRequired
from typing import TypedDict
from typing import Unpack
from zoneinfo import ZoneInfo
from zoneinfo import available_timezones

from .conf import TIME_ZONE
from .conf import UTC


def offset_display(delta: timedelta) -> str:
    seconds = delta.total_seconds()
    sign = "-" if seconds < 0 else "+"
    seconds = abs(seconds)
    hours = int(seconds // 3600)
    minutes = int(seconds // 60 % 60)
    if hours or minutes:
        return f"{sign}{hours:02}:{minutes:02}"
    else:
        return ""


def utcisoformat(dt) -> str:
    dt = adjust_dt(dt, tz=UTC)
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")


def utcnow() -> datetime:
    return datetime.now(tz=UTC)


def naivenow() -> datetime:
    return now().replace(tzinfo=None)


def now(tz: ZoneInfo = TIME_ZONE) -> datetime:
    return datetime.now(tz=tz)


def today(tz: ZoneInfo = TIME_ZONE) -> date:
    return now(tz).date()


class _ADJUST_DT_KWARGS(TypedDict):
    year: NotRequired[int]
    month: NotRequired[int]
    day: NotRequired[int]
    hour: NotRequired[int]
    minute: NotRequired[int]
    second: NotRequired[int]
    microsecond: NotRequired[int]
    fold: NotRequired[bool]


def adjust_dt(
    dt: datetime | date,
    *,
    assumed_tz: ZoneInfo | None = None,
    tz: tzinfo = TIME_ZONE,
    **fields: Unpack[_ADJUST_DT_KWARGS],
) -> datetime:
    """
    Args:
        dt: datetime to convert
        assumed_tz: assumed timezone if naive
        tz: target timezone

    Returns: timezone-aware datetime
    """

    if assumed_tz is None:
        assumed_tz = tz
    if not isinstance(dt, datetime):
        dt = datetime.combine(dt, time.min)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=assumed_tz)
    dt = dt.astimezone(tz)
    if fields:
        if "tzinfo" in fields:
            raise TypeError("Use `assumed_tz` or `tz` instead of `tzinfo`!")
        return dt.replace(**fields)
    else:
        return dt


cleanup_dt = partial(adjust_dt, microsecond=0)

time_strip_dt = partial(adjust_dt, hour=0, minute=0, second=0, microsecond=0)

BOOT_DT: datetime = utcnow()
BOOT_DT_NAIVE = BOOT_DT.replace(tzinfo=None)


TIMEZONES = [
    (name, f"(GMT{offset_display(offset)}) {name}")
    for offset, name in sorted(
        (BOOT_DT_NAIVE - BOOT_DT.astimezone(ZoneInfo(name)).replace(tzinfo=None), name) for name in available_timezones()
    )
]
