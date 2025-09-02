from datetime import UTC
from importlib.util import find_spec
from zoneinfo import ZoneInfo

if find_spec("django"):
    from django.conf import settings
else:
    settings = None

WSGI_BUFFER_INPUT_LIMIT = int(getattr(settings, "CSU_WSGI_BUFFER_INPUT_LIMIT", 25 * 1024 * 1024))
DRF_BEARER_TOKEN = getattr(settings, "CSU_DRF_BEARER_TOKEN", None)


if hasattr(settings, "TIME_ZONE"):
    TIME_ZONE = ZoneInfo(settings.TIME_ZONE)
else:
    TIME_ZONE = UTC

LOGGING_AUTH_INFO_FIELDS = getattr(settings, "CSU_LOGGING_AUTH_INFO_FIELDS", ("_auth",))
assert isinstance(LOGGING_AUTH_INFO_FIELDS, list | tuple), (
    f"Expected CSU_LOGGING_AUTH_INFO_FIELDS={LOGGING_AUTH_INFO_FIELDS!r} to be a list or tuple."
)
LOGGING_TB_LIMIT = getattr(settings, "CSU_LOGGING_TB_LIMIT", 5)
LOGGING_REQUEST_BODY_LIMIT = getattr(settings, "CSU_LOGGING_REQUEST_BODY_LIMIT", 102400)
LOGGING_RESPONSE_BODY_LIMIT = getattr(settings, "CSU_LOGGING_RESPONSE_BODY_LIMIT", 102400)
LOGGING_SHOW_HEADERS = getattr(settings, "CSU_LOGGING_SHOW_HEADERS", False)
