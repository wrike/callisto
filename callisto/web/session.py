from __future__ import annotations

import typing as t

import aiohttp.web as web

from ..libs.domains import consts
from . import get_pod_name


if t.TYPE_CHECKING:
    from ..libs.use_cases.session import SessionUseCase


async def create_session_handler(request: web.Request) -> web.Response:
    uc: SessionUseCase = request.app[consts.SESSION_USE_CASE_KEY]

    session_request = await request.json()

    data = await uc.create_session(session_request=session_request)

    return web.json_response(data=data)


async def delete_session_handler(request: web.Request) -> web.Response:
    uc: SessionUseCase = request.app[consts.SESSION_USE_CASE_KEY]

    data = await uc.delete_session(pod_name=get_pod_name(request))

    return web.json_response(data=data)
