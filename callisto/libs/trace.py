from __future__ import annotations

import typing as t
from contextvars import ContextVar
from uuid import uuid4


trace_id: ContextVar[str] = ContextVar('trace_id')
DEFAULT_WEB_HEADER = "X-Request-ID"

if t.TYPE_CHECKING:
    from aiohttp.web import Request


def get_trace_id_value(default: str = "DEFAULT") -> str:
    return trace_id.get(default)


def request_then_uuid_factory(header_name: str = DEFAULT_WEB_HEADER) -> t.Callable[[Request], str]:
    def request_then_uuid(request: Request) -> str:
        # extract marked trace id from request or generate a new one

        header_value = request.headers.get(header_name)
        uuid = header_value if header_value is not None else uuid4().hex

        return f"web-{uuid}"

    return request_then_uuid
