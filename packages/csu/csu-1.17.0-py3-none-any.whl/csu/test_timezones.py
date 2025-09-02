# ruff: noqa: DTZ001
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from .timezones import TIME_ZONE
from .timezones import UTC
from .timezones import adjust_dt


def as_tz(dt: datetime, tz):
    assert dt.tzinfo is None
    if hasattr(tz, "localize"):
        dt = tz.localize(dt, is_dst=None)
    else:
        dt = dt.replace(tzinfo=tz)
    dt = dt.astimezone(tz)
    if hasattr(tz, "normalize"):
        dt = tz.normalize(dt)
    return dt


def test_adjust_dt():
    assert adjust_dt(datetime(2020, 3, 7, 12, 35)) == as_tz(datetime(2020, 3, 7, 12, 35), TIME_ZONE)
    assert adjust_dt(datetime(2020, 3, 7, 12, 35, tzinfo=UTC)) == as_tz(datetime(2020, 3, 7, 14, 35), TIME_ZONE)
    assert adjust_dt(datetime(2020, 3, 7, 12, 35)) == as_tz(datetime(2020, 3, 7, 10, 35), UTC)


def test_adjust_dt_dst_pytz():
    pytz = pytest.importorskip("pytz")
    assert as_tz(datetime(2023, 3, 26), pytz.timezone("Europe/Bucharest")).isoformat() == "2023-03-26T00:00:00+02:00"
    assert as_tz(datetime(2023, 3, 27), pytz.timezone("Europe/Bucharest")).isoformat() == "2023-03-27T00:00:00+03:00"


def test_adjust_dt_dst():
    assert as_tz(datetime(2023, 3, 26), ZoneInfo("Europe/Bucharest")).isoformat() == "2023-03-26T00:00:00+02:00"
    assert as_tz(datetime(2023, 3, 27), ZoneInfo("Europe/Bucharest")).isoformat() == "2023-03-27T00:00:00+03:00"
    assert adjust_dt(datetime(2023, 3, 26)).isoformat() == "2023-03-26T00:00:00+02:00"
    assert adjust_dt(datetime(2023, 3, 27)).isoformat() == "2023-03-27T00:00:00+03:00"
