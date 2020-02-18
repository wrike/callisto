from __future__ import annotations

import typing as t

from aiohttp import hdrs

from ...exceptions import WebDriverException
from ...services.task_runner import TaskRunnerService


if t.TYPE_CHECKING:
    from .client import WebDriverClient


class WebDriverService:
    def __init__(self,
                 client: WebDriverClient,
                 task_runner_service: TaskRunnerService,
                 webdriver_path: str,
                 webdriver_port: int) -> None:
        self.client = client
        self.task_runner_service = task_runner_service
        self.webdriver_path = webdriver_path
        self.webdriver_port = webdriver_port

    async def create_session(self, pod_ip: str, session_request: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        api_url = f'http://{pod_ip}:{self.webdriver_port}{self.webdriver_path}/session'

        return await self.task_runner_service.run_with_retry(func=self.client.request,
                                                             tries=3,
                                                             pause=5,
                                                             retry_exc=WebDriverException,
                                                             url=api_url,
                                                             method=hdrs.METH_POST,
                                                             json=session_request)
