from __future__ import annotations

import typing as t

from aiohttp import StreamReader


if t.TYPE_CHECKING:
    from ..services.k8s.service import K8sService


class WebdriverLogsUseCase:
    def __init__(self, k8s_service: K8sService) -> None:
        self.k8s_service = k8s_service

    async def get_logs_stream(self, pod_name: str) -> StreamReader:
        return await self.k8s_service.get_pod_logs_stream(pod_name)
