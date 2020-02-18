from __future__ import annotations

import typing as t

import aiohttp.web as web

from ..libs.domains import consts


if t.TYPE_CHECKING:
    from ..libs.use_cases.health_check import HealthCheckUseCase


async def health_check_handler(request: web.Request) -> web.Response:
    uc: HealthCheckUseCase = request.app[consts.HEALTH_CHECK_USE_CASE_KEY]

    if await uc.is_healthy():
        status = web.HTTPOk.status_code
    else:
        status = web.HTTPServiceUnavailable.status_code

    return web.Response(status=status)
