from collections.abc import Iterable
from importlib.util import find_spec
from os import urandom

import httpx

from .timezones import naivenow

if find_spec("rest_framework"):
    from rest_framework.exceptions import APIException
    from rest_framework.status import HTTP_503_SERVICE_UNAVAILABLE
else:

    class APIException(Exception):
        pass

    HTTP_503_SERVICE_UNAVAILABLE = 503


def get_event_id():
    dt = naivenow()
    d = dt.date()
    t = dt.timestamp() % 86400
    return f"{d.year:2}{d.month:02}{d.day:02}:{urandom(4).hex()}:{t:08.2f}"


class TaggedError(Exception):
    def __init__(self, message, *details, event_id):
        super().__init__(message)
        self.event_id = event_id
        self.details = details
        if details:
            self.add_note(repr(details))

    def __str__(self):
        return f"{type(self).__name__}({', '.join(map(repr, self.args))})"

    def __repr__(self):
        details = [repr(arg) for arg in self.args]
        details.extend(repr(detail) for detail in self.details)
        details.append(f"event_id={self.event_id}")
        return f"{type(self).__name__}({', '.join(details)})"

    if not hasattr(Exception, "add_note"):

        def add_note(self, note: str):
            notes = getattr(self, "__notes__", None)
            if notes is None:
                self.__notes__ = [note]
            else:
                self.__notes__.append(note)


class RetryableError(TaggedError):
    """
    Either the service is down or temporarily broken (eg: 404/5xx states, malformed responses etc). Retryable.
    """


class HTTPErrorMixin:
    status_code: int
    response: httpx.Response

    def __init__(self, response: httpx.Response, message, *details, event_id):
        super().__init__(message, response.status_code, response.content, *details, event_id=event_id)
        self.status_code = response.status_code
        self.response = response


class InternalServiceError(TaggedError):
    """
    The service failed in handling (expected fields are missing, buggy code etc). Not retryable.
    """


class DecodeError(HTTPErrorMixin, InternalServiceError):
    """
    When content decoding fails.
    """

    def __init__(self, response: httpx.Response, error, *, event_id):
        super().__init__(response, error, event_id=event_id)
        self.error = error

    def __str__(self):
        return f"DecodeError({self.error!r}, response={self.response!r})"


class RetryableStatusError(HTTPErrorMixin, RetryableError):
    """
    When response status is bad, but retryable.
    """

    def __init__(self, response: httpx.Response, accept_statuses: set[int], retry_statuses: set[int], event_id):
        self.accept_statuses = sorted(accept_statuses)
        self.retry_statuses = sorted(retry_statuses)
        super().__init__(
            response,
            f"Received retryable status: {response.status_code} not in {self.accept_statuses} but in {self.retry_statuses}",
            event_id=event_id,
        )

    def __str__(self):
        return f"RetryableStatusError({self.response}, accept_statuses={self.accept_statuses}, retry_statuses={self.retry_statuses})"


class UnexpectedStatusError(HTTPErrorMixin, InternalServiceError):
    """
    When response status is bad.
    """

    def __init__(self, response: httpx.Response, accept_statuses: set[int], event_id):
        self.accept_statuses = sorted(accept_statuses)
        super().__init__(
            response,
            f"Received unexpected status: {response.status_code} not in {self.accept_statuses}",
            event_id=event_id,
        )

    def __str__(self):
        return f"UnexpectedStatusError({self.response}, accept_statuses={self.accept_statuses})"


class ExhaustedRetriesError(InternalServiceError):
    """
    The service reached the retry limit. Obviously not retryable.
    """

    def __init__(self, retries: int, *exceptions: list[Exception], event_id):
        super().__init__(f"Exhausted {retries} retries.", *exceptions, event_id=event_id)


class OpenServiceError(TaggedError):
    """
    The service failed in handling in a way that should be propagated upward the public API.

    The `event_id` is a mandatory parameter to encourage adding a relevant event_id if created from within a context.
    """

    message: str = "Unknown error"
    error_code: str = "unknown"
    status_code: int = HTTP_503_SERVICE_UNAVAILABLE

    def __init__(self, message=None, *, details: Iterable = (), event_id):
        super().__init__(str(message or self.message), *details, event_id=event_id)

    def as_api_service_error(self):
        exc = APIServiceError(
            self.message,
            error_code=self.error_code,
            status_code=self.status_code,
            event_id=self.event_id,
            cause=self,
        )
        return exc


class APIServiceError(APIException):
    status_code = HTTP_503_SERVICE_UNAVAILABLE
    accident_id_field = "accident_id"
    message_field = "detail"
    error_code_field = "code"

    def __init__(self, message, *, error_code="unavailable", status_code=None, event_id=None, cause=None, **kwargs):
        self.message = message
        self.code = error_code
        self.detail = {
            self.accident_id_field: get_event_id() if event_id is None else event_id,
            self.message_field: message,
            self.error_code_field: error_code,
            **kwargs,
        }
        if status_code:
            self.status_code = status_code
        if cause:
            self.__cause__ = cause
