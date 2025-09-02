import pytest

from .consts import REGISTRATION_NUMBER_RE

ROMANIAN_REGISTRATION_NUMBER_RE = REGISTRATION_NUMBER_RE["RO"]


@pytest.mark.parametrize(
    ("registration_number", "match"),
    [
        ("B03LRW", True),
        ("B100ABC", True),
        ("B010ABC", False),
        ("B001ABC", False),
        ("B01ABC", True),
        ("B00ABC", False),
        ("MM01ABC", True),
        ("MM00ABC", False),
        # red plates
        ("MM012", False),
        ("MM0123", False),
        ("MM01234", False),
        ("MM012345", False),
        ("B012", False),
        ("B0123", False),
        ("B01234", False),
        ("B012345", False),
        # long-term temporary
        ("MM123", False),
        ("MM1234", True),
        ("MM12345", True),
        ("MM123456", True),
        ("B123", False),
        ("B1234", True),
        ("B12345", True),
        ("B123456", True),
    ],
)
def test_registration_number_re_ro(registration_number, match):
    assert bool(ROMANIAN_REGISTRATION_NUMBER_RE.match(registration_number)) == match, f"{registration_number} expected {match} match"
