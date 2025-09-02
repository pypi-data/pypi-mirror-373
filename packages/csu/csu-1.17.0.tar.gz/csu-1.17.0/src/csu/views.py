import sys
from functools import cache
from functools import cached_property
from traceback import format_exception

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.http import HttpRequest
from django.http import HttpResponse
from django.utils.module_loading import import_string
from rest_framework import exceptions
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import set_rollback

from .conf import LOGGING_AUTH_INFO_FIELDS
from .conf import LOGGING_TB_LIMIT
from .consts import CONTEXT_LINE
from .consts import RESPONSE_EXCEPTION_LINE
from .consts import THICK_LINE
from .consts import TRACEBACK_LINE
from .exceptions import APIServiceError
from .exceptions import OpenServiceError
from .exceptions import TaggedError
from .exceptions import get_event_id
from .logging import default_logger
from .logging import get_content_lines
from .logging import get_request_line
from .service import HTTPService


class ServiceContextMixin:
    service_name: str

    @cached_property
    def service_instance(self):
        return self.get_service_instance(self.service_name)

    @staticmethod
    @cache
    def get_service_instance(service_name):
        service_class_path = getattr(settings, f"{service_name}_BACKEND")
        service_config = getattr(settings, f"{service_name}_CONFIG")
        service_class: type[HTTPService] = import_string(service_class_path)
        return service_class(service_config)

    def get_serializer_context(self):
        return {
            **super().get_serializer_context(),
            "service_instance": self.service_instance,
        }


class LoggingMixin:
    """
    A mixin class providing logic to log API requests.
    """

    logger = default_logger

    def finalize_response(self, request: Request | HttpRequest, response: Response | HttpResponse, *args, **kwargs):
        response: Response = super().finalize_response(request, response, *args, **kwargs)
        if not getattr(response, "exception", False):
            request_line, request_line_arguments = get_request_line(
                request.META,
                response.status_code,
                *(getattr(request, field, None) for field in LOGGING_AUTH_INFO_FIELDS),
            )
            content_lines, content_lines_arguments = get_content_lines(request, response)
            self.logger.info(f"{request_line}{content_lines}", *request_line_arguments, *content_lines_arguments)
        return response


def exception_handler(
    exc,
    context,
    event_id_field="accident_id",
    message_field="detail",
    error_error_code_field="code",
):
    """
    Returns the response that should be used for any given exception.

    By default, we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    if isinstance(exc, TaggedError):
        event_id = exc.event_id
    else:
        event_id = None

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()
    elif isinstance(exc, OpenServiceError):
        exc = exc.as_api_service_error()

    headers = {}
    if isinstance(exc, exceptions.APIException):
        if auth_header := getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = auth_header
        if wait := getattr(exc, "wait", None):
            headers["Retry-After"] = f"{wait:d}"
        status_code = exc.status_code
    else:
        status_code = 500

    request = context.get("request")

    if request:
        request_line, request_line_arguments = get_request_line(request.META, status_code)
        content_lines, content_lines_arguments = get_content_lines(request, thick_line=False)
    else:
        request_line, request_line_arguments = "", ()
        content_lines, content_lines_arguments = "", ()
    if isinstance(exc, exceptions.ValidationError):
        # We don't want to patch up regular validation error responses.
        data = exc.detail
    elif isinstance(exc, APIServiceError):
        data = exc.detail
    elif isinstance(exc, exceptions.APIException):
        detail = exc.detail
        data = {
            event_id_field: event_id or get_event_id(),
            message_field: detail,
            error_error_code_field: detail.code,
        }
    else:
        data = {
            event_id_field: event_id or get_event_id(),
            message_field: "Internal server error.",
            error_error_code_field: "server",
        }

    accepted_renderer = getattr(request, "accepted_renderer", None)
    (default_logger.warning if status_code < 500 else default_logger.error)(
        f"{request_line} (renderer: %s){content_lines}\n%s\n  %s\n%s\n%s\n%s\n  %s\n%s",
        *request_line_arguments,
        type(accepted_renderer).__name__,
        *content_lines_arguments,
        CONTEXT_LINE,
        context,
        TRACEBACK_LINE,
        "".join(format_exception(exc, limit=-LOGGING_TB_LIMIT)).strip(),
        RESPONSE_EXCEPTION_LINE,
        data,
        THICK_LINE,
        exc_info=True,
        extra={"csu_exc": True},
    )
    set_rollback()
    response = Response(data, status=status_code, headers=headers)
    accepted_renderer = getattr(request, "accepted_renderer", None)
    if not accepted_renderer:
        accepted_renderer = JSONRenderer()
    response.accepted_renderer = accepted_renderer
    response.accepted_media_type = accepted_renderer.media_type
    response.renderer_context = context
    return response


def server_error(request, *args, **kwargs):
    """
    Generic 500 error handler.
    """
    context = {"request": request}
    _, exc, _ = sys.exc_info()
    return exception_handler(exc, context)
