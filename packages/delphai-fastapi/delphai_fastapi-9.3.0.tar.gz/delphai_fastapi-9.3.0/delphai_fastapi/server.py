import asyncio
import hypercorn.asyncio
import logging
import signal


async def serve_http(app, port=8000):
    config = hypercorn.Config()
    config.bind = [f"0.0.0.0:{int(port)}"]
    config.accesslog = logging.getLogger("hypercorn.access")
    config.access_log_format = '[%(s)s] %(m)s %(U)s?%(q)s [%(L)ss] %(b)s "%(h)s"'
    config.errorlog = logging.getLogger("hypercorn.error")

    shutdown_trigger = None
    has_custom_handlers = any(
        signal.getsignal(signum) not in {signal.default_int_handler, signal.SIG_DFL}
        for signum in (signal.SIGINT, signal.SIGTERM)
    )
    if has_custom_handlers:
        # prevent hypercorn from catching `SIGTERM` and `SIGINT` if
        # other signal handlers are already installed elsewhere.
        shutdown_trigger = asyncio.Event().wait

    await hypercorn.asyncio.serve(app, config, shutdown_trigger=shutdown_trigger)
