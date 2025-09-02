import time_machine

from . import exceptions
from .exceptions import get_event_id


def test_get_accident_id(monkeypatch):
    monkeypatch.setattr(exceptions, "urandom", lambda len: bytes(range(len)))
    with time_machine.travel(1674777700.5816755):
        assert get_event_id() == "20230127:00010203:00100.58"
