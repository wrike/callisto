from __future__ import annotations

import typing as t

import aiohttp.web as web

from ..libs.domains import consts


if t.TYPE_CHECKING:
    from ..libs.use_cases.status import StatusUseCase


async def status_handler(request: web.Request) -> web.Response:
    uc: StatusUseCase = request.app[consts.STATUS_USE_CASE_KEY]

    status_data = uc.get_status()

    return web.json_response(data=status_data)
