from __future__ import annotations

import typing as t

import aiohttp.web as web

from ...libs.middleware import error_middleware, tracing_middleware_factory
from ...libs.trace import request_then_uuid_factory, trace_id
from ...web.routes import setup_routes
from .logger import logger


async def run_api(*,
                  host: str,
                  port: int,
                  app_state: t.Mapping[str, t.Any]) -> web.AppRunner:
    app = web.Application(
        middlewares=[tracing_middleware_factory(trace_id, request_then_uuid_factory()),  # type: ignore
                     error_middleware])  # type: ignore

    app.update(app_state)
    setup_routes(app)

    runner = web.AppRunner(app, access_log=False, handle_signals=True)
    await runner.setup()

    site = web.TCPSite(runner, host, port)
    await site.start()

    logger.info(f"======== Running on {site.name} ========")

    return runner
