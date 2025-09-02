from asgiref.typing import ASGIReceiveCallable
from asgiref.typing import ASGISendCallable
from asgiref.typing import Scope
from django.core.asgi import get_asgi_application

from . import logger


def get_worker_lifespan_application():
    django_application = get_asgi_application()

    async def application_with_worker_lifespan(scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] == "lifespan":
            try:
                from .registry import REGISTRY  # noqa:PLC0415

                while True:
                    message = await receive()
                    message_type = message["type"]
                    if message_type == "lifespan.startup":
                        logger.info("Found %s registered engines.", len(REGISTRY))
                        for module_name, engine in REGISTRY.items():
                            logger.info("Starting engine for %s: %s...", module_name, engine)
                            await engine.start()
                        await send({"type": "lifespan.startup.complete"})
                    if message_type == "lifespan.shutdown":
                        for engine in REGISTRY.values():
                            await engine.stop()
                        await send({"type": "lifespan.shutdown.complete"})
                        return
            except Exception as exc:
                logger.exception("Failed setting up lifespan: %r", exc)
        else:
            await django_application(scope, receive, send)

    return application_with_worker_lifespan
