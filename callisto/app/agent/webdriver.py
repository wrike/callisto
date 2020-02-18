from __future__ import annotations

from ...libs.domains.config import PodConfig
from ...libs.services.task_runner import TaskRunnerService
from ...libs.services.webdriver.client import WebDriverClient
from ...libs.services.webdriver.service import WebDriverService


def init_webdriver_service(task_runner_service: TaskRunnerService, pod_config: PodConfig) -> WebDriverService:
    return WebDriverService(client=WebDriverClient(),
                            task_runner_service=task_runner_service,
                            webdriver_path=pod_config.webdriver_path,
                            webdriver_port=pod_config.webdriver_port)
