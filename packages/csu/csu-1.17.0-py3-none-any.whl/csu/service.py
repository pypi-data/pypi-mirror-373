import os
from dataclasses import dataclass
from decimal import Decimal
from logging import Logger
from logging import getLogger
from traceback import format_exc
from typing import Any

import httpx

from .consts import LINE_LENGTH
from .consts import REQUEST_CONTENT_LINE
from .consts import THICK_LINE
from .exceptions import DecodeError
from .exceptions import ExhaustedRetriesError
from .exceptions import InternalServiceError
from .exceptions import OpenServiceError
from .exceptions import RetryableError
from .exceptions import RetryableStatusError
from .exceptions import UnexpectedStatusError
from .exceptions import get_event_id


@dataclass(kw_only=True)
class HTTPServiceResponse:
    status: int
    httpx_response: httpx.Response
    event_id: str
    json: None | list | dict = None

    def __getattr__(self, name):
        return getattr(self.httpx_response, name)


class HTTPServiceContext:
    client_class = httpx.Client
    client: httpx.Client | httpx.AsyncClient
    logger: Logger
    response_content_log_limit = 10240
    request_content_log_limit = None

    def __init__(self, service: "HTTPService", event_id=None, **kwargs):
        kwargs.setdefault("auth", HTTPServiceAuth(self, service))
        self.client = self.client_class(
            event_hooks={"request": [self.log_request], "response": [self.log_response]},
            timeout=service.timeout,
            verify=service.verify,
            cert=service.cert,
            base_url=service.base_url,
            **kwargs,
        )
        self.logger = service.logger
        self.retries = service.retries
        if event_id:
            if ":" not in event_id:
                raise ValueError("Expected a 'date:random:time' structured event id.")
        else:
            event_id = get_event_id()
        date, self.short_id = event_id.split(":", 1)
        self.event_id = f"{date}:{self.short_id}"

    def __enter__(self):
        self.client.__enter__()
        return self

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    def log_request(self, request: httpx.Request):
        request.read()
        self.handle_log_request(request)

    def handle_log_request(self, request: httpx.Request):
        auth = request.headers.get("authorization", "")
        if request.content:
            size = len(request.content)
            limit = self.request_content_log_limit
            if limit and size > limit:
                content = f"{request.content!r:.{limit}}\n   ... {size - limit} more bytes"
            else:
                content = f"{request.content!r}"

            self.logger.info(
                "[%s] %s %s +[%s]\n%s\n   %s\n%s",
                self.short_id,
                request.method,
                request.url,
                auth,
                REQUEST_CONTENT_LINE,
                content,
                THICK_LINE,
            )
        else:
            self.logger.info(
                "[%s] %s %s +[%s]",
                self.short_id,
                request.method,
                request.url,
                auth,
            )

    def log_response(self, response: httpx.Response):
        response.read()
        self.handle_log_response(response)

    def handle_log_response(self, response: httpx.Response):
        size = len(response.content)
        encoding = response.encoding or "no encoding"
        charset = response.charset_encoding or "no charset"
        response_line = f" response body {encoding}: {charset} - {size} bytes ".center(LINE_LENGTH, "-")
        limit = self.response_content_log_limit
        if limit and size > limit:
            content = f"{response.content!r:.{limit}}\n   ... {size - limit} more bytes"
        else:
            content = f"{response.content!r}"
        self.logger.info(
            "[%s] %s %s => %s\n%s\n  %s\n%s",
            self.short_id,
            response.request.method,
            response.url,
            response.status_code,
            response_line,
            content,
            THICK_LINE,
        )

    def __exit__(self, exc_type, exc_val: Exception, exc_tb):
        self.client.__exit__(exc_type, exc_val, exc_tb)
        self.handle_exit(exc_type, exc_val, exc_tb)

    def handle_exit(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return
        else:
            self.logger.warning("[%s] __exit__ !> %r", self.short_id, exc_val)

    def handle_process_response(
        self, response: httpx.Response, *, retry_statuses: set[int], accept_statuses: set[int], expect_json
    ) -> HTTPServiceResponse:
        if response.status_code in retry_statuses:
            raise RetryableStatusError(response, accept_statuses, retry_statuses, event_id=self.event_id)
        elif response.status_code not in accept_statuses:
            raise UnexpectedStatusError(response, accept_statuses, event_id=self.event_id)

        if expect_json:
            try:
                json = response.json(parse_float=Decimal)
            except Exception as exc:
                raise DecodeError(response, exc, event_id=self.event_id) from None
        else:
            json = None

        return HTTPServiceResponse(
            status=response.status_code,
            httpx_response=response,
            json=json,
            event_id=self.event_id,
        )

    def handle_prepare_request(
        self,
        method,
        url,
        *,
        accept_statuses: set[int],
        expect_json: bool,
        follow_redirects: bool,
        retries_left: int,
        retry_count: int,
        retry_statuses: set[int],
        retry: bool,
        **kwargs,
    ):
        return self.client.build_request(method, url, **kwargs)

    def request(
        self,
        method,
        url,
        *,
        accept_statuses=(200,),
        expect_json=True,
        follow_redirects=False,
        retry_statuses=(500, 502, 503, 504),
        retry=True,
        **kwargs,
    ) -> HTTPServiceResponse:
        retry_statuses = set(retry_statuses)
        accept_statuses = set(accept_statuses)
        assert not (common := sorted(retry_statuses & accept_statuses)), f"{common} is in both retry_statuses and accept_statuses!"
        retry_failures = []
        for retries_left in reversed(range(self.retries if retry else 1)):
            request = self.handle_prepare_request(
                method,
                url,
                accept_statuses=accept_statuses,
                expect_json=expect_json,
                follow_redirects=follow_redirects,
                retries_left=retries_left,
                retry_statuses=retry_statuses,
                retry_count=(self.retries - 1 - retries_left) if retry else 0,
                retry=retry,
                **kwargs,
            )
            try:
                return self.handle_process_response(
                    self.client.send(
                        request,
                        follow_redirects=follow_redirects,
                    ),
                    retry_statuses=retry_statuses,
                    accept_statuses=accept_statuses,
                    expect_json=expect_json,
                )
            except (httpx.RequestError, RetryableError) as exc:
                retry_failures.append(exc)
                if retries_left:
                    self.logger.error(
                        "[%s] %s %s !> %r (will retry %s more times)\n%s",
                        self.short_id,
                        method,
                        request.url,
                        exc,
                        retries_left,
                        format_exc(limit=5),
                    )
                else:
                    if retry:
                        self.logger.error("[%s] %s %s !> %r (exhausted retries)", self.short_id, method, request.url, exc)
                    else:
                        self.logger.error("[%s] %s %s !> %r (no retry)", self.short_id, method, request.url, exc)
                        raise InternalServiceError(exc, event_id=self.event_id) from exc
            except (InternalServiceError, OpenServiceError) as exc:
                self.logger.exception("[%s] %s %s !> failed: %r", self.short_id, method, request.url, exc)
                raise
            except Exception as exc:
                self.logger.error("[%s] %s %s !> %r (not retryable)", self.short_id, method, request.url, exc)
                raise InternalServiceError(exc, event_id=self.event_id) from exc
        else:
            raise ExhaustedRetriesError(self.retries, *retry_failures, event_id=self.event_id)


class AsyncHTTPServiceContext(HTTPServiceContext):
    client_class = httpx.AsyncClient
    client: httpx.AsyncClient
    logger: Logger

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def log_request(self, request: httpx.Request):
        await request.aread()
        self.handle_log_request(request)

    async def log_response(self, response: httpx.Response):
        await response.aread()
        self.handle_log_response(response)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)
        self.handle_exit(exc_type, exc_val, exc_tb)

    async def request(
        self,
        method,
        url,
        *,
        accept_statuses=(200,),
        expect_json=True,
        follow_redirects=False,
        retry_statuses=(500, 502, 503, 504),
        retry=True,
        **kwargs,
    ) -> HTTPServiceResponse:
        retry_failures = []
        for retries_left in reversed(range(self.retries if retry else 1)):
            request = self.client.build_request(method, url, **kwargs)
            try:
                return self.handle_process_response(
                    await self.client.send(
                        request,
                        follow_redirects=follow_redirects,
                    ),
                    retry_statuses=retry_statuses,
                    accept_statuses=accept_statuses,
                    expect_json=expect_json,
                )
            except (httpx.RequestError, RetryableError) as exc:
                retry_failures.append(exc)
                if retries_left:
                    self.logger.error(
                        "[%s] %s %s !> %r (will retry %s more times)\n%s",
                        self.short_id,
                        method,
                        request.url,
                        exc,
                        retries_left,
                        format_exc(limit=5),
                    )
                else:
                    if retry:
                        self.logger.error("[%s] %s %s !> %r (exhausted retries)", self.short_id, method, request.url, exc)
                    else:
                        self.logger.error("[%s] %s %s !> %r (no retry)", self.short_id, method, request.url, exc)
                        raise InternalServiceError(exc, event_id=self.event_id) from exc
            except (InternalServiceError, OpenServiceError) as exc:
                self.logger.exception("[%s] %s %s !> failed: %r", self.short_id, method, request.url, exc)
                raise
            except Exception as exc:
                self.logger.error("[%s] %s %s !> %r (not retryable)", self.short_id, method, request.url, exc)
                raise InternalServiceError(exc, event_id=self.event_id) from exc
        else:
            raise ExhaustedRetriesError(*retry_failures, event_id=self.event_id)


class HTTPService:
    context_class: type[HTTPServiceContext] = HTTPServiceContext
    logger_name: str = "service"
    logger: Logger
    base_url: str
    timeout: int
    retries: int
    verify: bool
    cert: str

    def __init__(self, config: dict[str, Any]):
        self.base_url = config["BASE_URL"]
        self.timeout = config.get("TIMEOUT", 60)
        self.retries = config.get("RETRIES", 3)
        self.verify = config.get("VERIFY", True)
        self.cert = config.get("CERT")
        self.logger = getLogger(self.logger_name)
        self.logger.info(
            "[pid:%s] Setting up %s with BASE_URL=%r TIMEOUT=%s RETRIES=%s VERIFY=%s",
            os.getpid(),
            type(self).__name__,
            self.base_url,
            self.timeout,
            self.retries,
            self.verify,
        )

    def context(self, **kwargs):
        return self.context_class(self, **kwargs)

    def auth(self, request: httpx.Request, context: HTTPServiceContext):
        yield request


class AsyncHTTPService(HTTPService):
    context_class: type[AsyncHTTPServiceContext] = AsyncHTTPServiceContext

    def auth(self, request: httpx.Request, context: AsyncHTTPServiceContext):
        yield request


class HTTPServiceAuth(httpx.Auth):
    context: HTTPServiceContext | AsyncHTTPServiceContext
    service: HTTPService

    def __init__(self, context: HTTPServiceContext | AsyncHTTPServiceContext, service: HTTPService):
        self.context = context
        self.service = service

    def auth_flow(self, request: httpx.Request):
        yield from self.service.auth(request, self.context)
