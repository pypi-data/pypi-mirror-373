from io import BytesIO

from .conf import WSGI_BUFFER_INPUT_LIMIT
from .consts import REQUEST_OVERSIZE_LINE
from .consts import THICK_LINE
from .logging import default_logger
from .logging import get_request_line


def buffer_input(app, limit=WSGI_BUFFER_INPUT_LIMIT, size=1024 * 1024):
    """
    Required for LoggingMixin to be able to log raw input (useful for debugging decoding failures).
    """

    def buffer_input_middle(environ, start_response):
        buffer = BytesIO()
        stream = environ["wsgi.input"]
        while buffer.tell() < limit:
            chunk = stream.read(size)
            if chunk:
                buffer.write(chunk)
            else:
                buffer.seek(0)
                break
        else:
            format, arguments = get_request_line(environ, 400, auth="*")
            default_logger.error(f"REQUEST BODY OVERSIZE: {format}", *arguments)
            buffer.seek(0)
            first10kb = buffer.read(10240)
            format, arguments = get_request_line(environ, 400)
            arguments += REQUEST_OVERSIZE_LINE, first10kb, environ.get("CONTENT_LENGTH"), THICK_LINE
            format += "\n%s\n%s -- Content-Length: %s\n%s"
            default_logger.info(format, *arguments)
            start_response("400 Bad Request", [])
            return [b"Oversize."]
        environ["wsgi.input"] = buffer
        del buffer
        return app(environ, start_response)

    return buffer_input_middle
