import logging
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from csu import exceptions


@pytest.fixture(scope="session")
def vcr_config():
    return {
        "decode_compressed_response": True,
        "match_on": ("method", "scheme", "host", "path", "query"),  # no port because it's random
    }


@pytest.fixture
def fake_accident_id(monkeypatch):
    calls = []

    def fake_urandom(_):
        frame = sys._getframe().f_back.f_back
        filename = Path(frame.f_code.co_filename).name
        calls.append(f"{filename}:{frame.f_lineno}")
        return bytes([len(calls)])

    monkeypatch.setattr(exceptions, "naivenow", lambda: datetime(2024, 12, 12))  # noqa: DTZ001
    monkeypatch.setattr(exceptions, "urandom", fake_urandom)
    return SimpleNamespace(
        calls=calls,
    )


@pytest.fixture
def caplogs(caplog):
    def get_logs():
        logs = "\n".join(f"{record.levelname:7} | {record.message}" for record in caplog.records)
        print(logs)
        return logs

    with caplog.at_level(logging.INFO, logger="service"):
        yield SimpleNamespace(
            get=get_logs,
        )
