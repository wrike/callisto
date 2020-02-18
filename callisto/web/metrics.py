from __future__ import annotations

import typing as t

import aiohttp.web as web

from ..libs.domains import consts


if t.TYPE_CHECKING:
    from ..libs.use_cases.metrics import MetricsUseCase


async def metrics_handler(request: web.Request) -> web.Response:
    uc: MetricsUseCase = request.app[consts.METRICS_USE_CASE_KEY]

    return await uc.get_metrics()
