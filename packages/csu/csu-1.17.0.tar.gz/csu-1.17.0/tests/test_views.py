import json
from functools import partial

import pytest

pytest.importorskip("rest_framework")
from rest_framework import exceptions
from rest_framework.response import Response

from csu import views


def test_exception_handler(fake_accident_id):
    resp: Response
    exception_handler = partial(
        views.exception_handler,
        event_id_field="accident_id",
        message_field="error_message",
        error_error_code_field="error_code",
    )

    resp = exception_handler(exceptions.APIException("foo", "bar"), {})
    assert resp.status_code == 500
    assert json.dumps(resp.data) == '{"accident_id": "20241212:01:79200.00", "error_message": "foo", "error_code": "bar"}'

    resp = exception_handler(exceptions.ValidationError("foo"), {})
    assert resp.status_code == 400
    assert resp.data == ["foo"]

    resp = exception_handler(exceptions.ValidationError({"foo": [123]}), {})
    assert resp.status_code == 400
    assert resp.data == {
        "foo": ["123"],
    }

    resp = exception_handler(exceptions.AuthenticationFailed("foo"), {})
    assert resp.status_code == 401
    assert resp.data == {
        "accident_id": "20241212:02:79200.00",
        "error_code": "authentication_failed",
        "error_message": "foo",
    }

    resp = exception_handler(exceptions.PermissionDenied("foo"), {})
    assert resp.status_code == 403
    assert resp.data == {
        "accident_id": "20241212:03:79200.00",
        "error_code": "permission_denied",
        "error_message": "foo",
    }

    resp = exception_handler(exceptions.NotFound("foo"), {})
    assert resp.status_code == 404
    assert resp.data == {
        "accident_id": "20241212:04:79200.00",
        "error_code": "not_found",
        "error_message": "foo",
    }

    resp = exception_handler(exceptions.MethodNotAllowed("XXX"), {})
    assert resp.status_code == 405
    assert resp.data == {
        "accident_id": "20241212:05:79200.00",
        "error_code": "method_not_allowed",
        "error_message": 'Method "XXX" not allowed.',
    }

    resp = exception_handler(exceptions.NotAcceptable("foo", "bar"), {})
    assert resp.status_code == 406
    assert resp.data == {
        "accident_id": "20241212:06:79200.00",
        "error_code": "bar",
        "error_message": "foo",
    }

    resp = exception_handler(exceptions.UnsupportedMediaType("foo/bar"), {})
    assert resp.status_code == 415
    assert resp.data == {
        "accident_id": "20241212:07:79200.00",
        "error_code": "unsupported_media_type",
        "error_message": 'Unsupported media type "foo/bar" in request.',
    }

    resp = exception_handler(exceptions.Throttled(123), {})
    assert resp.status_code == 429
    assert resp.data == {
        "accident_id": "20241212:08:79200.00",
        "error_code": "throttled",
        "error_message": "Request was throttled. Expected available in 123 seconds.",
    }
