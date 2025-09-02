from base64 import b64decode
from logging import Formatter
from logging import getLogger

from django.conf import settings
from django.core.handlers.asgi import ASGIRequest
from django.http import HttpRequest
from django.http import HttpResponse
from rest_framework.request import Empty
from rest_framework.request import Request
from rest_framework.response import Response

from .conf import LOGGING_REQUEST_BODY_LIMIT
from .conf import LOGGING_RESPONSE_BODY_LIMIT
from .conf import LOGGING_SHOW_HEADERS
from .consts import LINE_LENGTH
from .consts import REQUEST_DATA_LINE
from .consts import RESPONSE_CONTENT_LINE
from .consts import RESPONSE_DATA_LINE
from .consts import RESPONSE_LINE
from .consts import RESPONSE_UNKNOWN_LINE
from .consts import THICK_LINE

default_logger = getLogger("csu")


def get_remote_addresses(environ, placeholder=None):
    remote_addr = [environ.get("REMOTE_ADDR", placeholder)]
    forwarded_for = environ.get("HTTP_X_FORWARDED_FOR", "").split(",")
    if forwarded_for:
        forwarded_for.extend(remote_addr)
        remote_addr = list(filter(None, (ip.strip() for ip in forwarded_for)))
    return remote_addr


def get_request_line(environ, status_code, auth=None, *extra_auth):
    auth_info = []
    if auth:
        auth_info.append(auth)
    else:
        auth = environ.get("HTTP_AUTHORIZATION", "")
        if isinstance(auth, bytes):
            auth = auth.decode()
        auth, _, details = auth.partition(" ")
        if auth.lower() == "basic":
            try:
                user, *_ = b64decode(details).decode().partition(":")
            except Exception as exc:
                auth_info.extend((auth, exc, details))
            else:
                auth_info.extend((auth, user))
        else:
            auth_info.extend((auth, details))

    auth_info.extend(extra_auth)
    if query := environ.get("QUERY_STRING"):
        query = f"?{query}"
    else:
        query = ""
    format = f'"{environ["REQUEST_METHOD"]} {environ["PATH_INFO"]}%s" {status_code} +[%s] @%s'
    remote_addr = " via ".join(get_remote_addresses(environ, placeholder="?"))
    arguments = [query, ";".join(str(item) for item in auth_info if item), remote_addr]
    return format, arguments


def get_content_lines(request: Request | HttpRequest | ASGIRequest, response: Response | HttpResponse | None = None, thick_line=True):
    if hasattr(request, "environ"):
        stream = request.environ["wsgi.input"]
    else:
        # ASGIRequest or Request wrapping ASGIRequest
        stream = request._stream
    try:
        stream.seek(0)
    except (OSError, AttributeError):
        buffered = False
    else:
        buffered = True
    if buffered and (body := stream.read()):
        parser_context = getattr(request, "parser_context", {})
        encoding = parser_context.get("encoding", settings.DEFAULT_CHARSET)
        arguments = f" request body ({encoding}: {request.content_type}) ".center(LINE_LENGTH, "-"), body
        format = f"\n%s\n  %.{LOGGING_REQUEST_BODY_LIMIT}s"
    elif getattr(request, "_body", None):
        arguments = f" request body ({request.content_type}) ".center(LINE_LENGTH, "-"), request._body
        format = f"\n%s\n  %.{LOGGING_REQUEST_BODY_LIMIT}s"
    elif getattr(request, "_data", None) and request._data is not Empty:
        arguments = REQUEST_DATA_LINE, request._data
        format = f"\n%s\n  %.{LOGGING_REQUEST_BODY_LIMIT}s"
    else:
        arguments = ()
        format = ""
    if LOGGING_SHOW_HEADERS:
        format += "\n%s\n  %s"
        arguments += (
            " request headers ".center(LINE_LENGTH, "-"),
            "\n  ".join(f"{name}: {value}" for name, value in request.headers.items()),
        )
    if response:
        try:
            if getattr(response, "is_rendered", True) and response.content:
                arguments += RESPONSE_CONTENT_LINE, response.content
                format += f"\n%s\n  %.{LOGGING_RESPONSE_BODY_LIMIT}r"
            elif hasattr(response, "data") and response.data is not None:
                arguments += RESPONSE_DATA_LINE, response.data
                format += f"\n%s\n  %.{LOGGING_RESPONSE_BODY_LIMIT}r"
            else:
                arguments += RESPONSE_LINE, response
                format += f"\n%s\n  %.{LOGGING_RESPONSE_BODY_LIMIT}r"
        except Exception as exc:
            arguments += RESPONSE_UNKNOWN_LINE, exc
            format += "\n%s\n  Failed to get response: %s"
    if arguments and thick_line:
        format += "\n%s"
        arguments += (THICK_LINE,)
    return format, arguments


class ViewErrorFormatter(Formatter):
    """
    Formatter that fixes up the record so the traceback does not appear two times.
    """

    def __init__(self, fmt="[%(asctime)s.%(msecs)d] %(name)s (%(levelname)s) %(message)s", datefmt="%Y-%m-%d %H:%M:%S", **kwargs):
        super().__init__(fmt=fmt, datefmt=datefmt, **kwargs)

    def format(self, record):
        if getattr(record, "csu_exc", False):
            record.exc_text = "\n"
        return super().format(record)
