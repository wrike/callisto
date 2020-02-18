from __future__ import annotations

import aiohttp.web as web

from ..libs.domains import consts
from ..libs.use_cases.webdriver_logs import WebdriverLogsUseCase
from . import get_pod_name


async def webdriver_logs_handler(request: web.Request) -> web.WebSocketResponse:
    uc: WebdriverLogsUseCase = request.app[consts.WEBDRIVER_LOGS_USE_CASE_KEY]

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for line in await uc.get_logs_stream(pod_name=get_pod_name(request)):
        if line:
            await ws.send_bytes(line)
        else:
            await ws.close()
            break

    return ws
