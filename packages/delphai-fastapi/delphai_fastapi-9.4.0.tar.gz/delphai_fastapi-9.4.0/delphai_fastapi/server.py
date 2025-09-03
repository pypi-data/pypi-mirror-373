import asyncio
import logging
import signal
import typing

import hypercorn.asyncio


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


async def run_forever(*coros: typing.Coroutine) -> None:
    loop = asyncio.get_running_loop()
    signal_event = asyncio.Event()

    for signum in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(signum, signal_event.set)

    try:
        tasks = [asyncio.ensure_future(coro) for coro in coros]

        await asyncio.wait(
            [asyncio.ensure_future(signal_event.wait()), *tasks],
            return_when=asyncio.FIRST_COMPLETED,
        )
    finally:
        for signum in (signal.SIGINT, signal.SIGTERM):
            loop.remove_signal_handler(signum)

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)
