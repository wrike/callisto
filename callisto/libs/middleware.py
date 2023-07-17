from __future__ import annotations

import typing as t
from contextlib import contextmanager

from aiohttp.web import (
    HTTPInternalServerError,
    json_response,
    middleware,
)

from .services.log import logger


if t.TYPE_CHECKING:
    from contextvars import ContextVar

    from aiohttp.web import Request, Response

    AiohttpHandler = t.Callable[[Request], t.Awaitable[Response]]
    MiddlewereHandler = t.Callable[[Request, AiohttpHandler], t.Awaitable[Response]]

T = t.TypeVar("T")


@middleware
async def error_middleware(request: Request, handler: t.Callable[[Request], t.Awaitable[Response]]) -> Response:
    """logs an exception and returns an error message to the client"""
    try:
        return await handler(request)
    except Exception as e:
        logger.exception(e)
        return json_response(text=str(e), status=HTTPInternalServerError.status_code)


@contextmanager
def tracing_context(variable: ContextVar[T], value: T) -> t.Generator[None, None, None]:
    token = variable.set(value)

    try:
        yield
    finally:
        variable.reset(token)


def tracing_middleware_factory(variable: ContextVar[T], trace_id_getter: t.Callable[[Request], T]) -> MiddlewereHandler:
    @middleware
    async def middleware_handler(request: Request, handler: AiohttpHandler) -> Response:
        """Add trace ids to web requests."""

        with tracing_context(variable, trace_id_getter(request)):
            return await handler(request)

    return middleware_handler
