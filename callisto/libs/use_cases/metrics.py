from __future__ import annotations

import typing as t

import aiohttp.web as web
from prometheus_client.exposition import CONTENT_TYPE_LATEST  # type: ignore


if t.TYPE_CHECKING:
    from ..services.state import StateService


class MetricsUseCase:
    def __init__(self, state_service: StateService) -> None:
        self.state_service = state_service

    async def get_metrics(self) -> web.Response:
        metrics = await self.state_service.collect_metrics()

        # cannot fill Content-type with content_type argument of the Response.__init__,
        # as CONTENT_TYPE_LATEST includes more than just content type... (charset etc.)
        return web.Response(body=metrics, headers={'Content-type': CONTENT_TYPE_LATEST})
