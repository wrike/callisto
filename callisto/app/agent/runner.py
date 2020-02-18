from __future__ import annotations

import typing as t

from ...libs.domains import consts
from ...libs.domains.config import (
    K8sConfig,
    PodConfig,
    WebOptions,
)
from ...libs.domains.logging import GraylogParameters
from ...libs.use_cases.health_check import HealthCheckUseCase
from ...libs.use_cases.metrics import MetricsUseCase
from ...libs.use_cases.session import SessionUseCase
from ...libs.use_cases.status import StatusUseCase
from ...libs.use_cases.webdriver_logs import WebdriverLogsUseCase
from .api import run_api
from .k8s import init_k8s_service
from .logger import get_default_logging_config, init_logger
from .scheduler import init_scheduler
from .sentry import init_sentry
from .state import init_state_service
from .task_runner import init_task_runner_service
from .webdriver import init_webdriver_service


async def run_agent(web_parameters: WebOptions,
                    log_level: int,
                    k8s_config: K8sConfig,
                    pod_config: PodConfig,
                    instance_id: str,
                    sentry_dsn: str,
                    graylog_config: t.Optional[GraylogParameters],
                    ) -> t.Callable[[], t.Awaitable[None]]:
    init_logger(config=get_default_logging_config(instance_id=instance_id, graylog_config=graylog_config),
                log_level=log_level)
    init_sentry(sentry_dsn=sentry_dsn, instance_id=instance_id)

    scheduler = await init_scheduler()
    task_runner_service = await init_task_runner_service(scheduler)
    k8s_service = await init_k8s_service(k8s_config=k8s_config, task_runner_service=task_runner_service)
    state_service = init_state_service(k8s_service=k8s_service, instance_id=instance_id)

    webdriver_service = init_webdriver_service(task_runner_service, pod_config=pod_config)

    web_runner = await run_api(
        host=web_parameters.host,
        port=web_parameters.port,
        app_state={
            consts.HEALTH_CHECK_USE_CASE_KEY: HealthCheckUseCase(),
            consts.METRICS_USE_CASE_KEY: MetricsUseCase(state_service=state_service),
            consts.SESSION_USE_CASE_KEY: SessionUseCase(k8s_service=k8s_service,
                                                        webdriver_service=webdriver_service,
                                                        pod_config=pod_config,
                                                        state_service=state_service,
                                                        task_runner_service=task_runner_service),
            consts.STATUS_USE_CASE_KEY: StatusUseCase(state_service=state_service),
            consts.WEBDRIVER_LOGS_USE_CASE_KEY: WebdriverLogsUseCase(k8s_service),
        }
    )

    return on_close((
        scheduler.close,
        web_runner.cleanup,
    ))


def on_close(close_cbks: t.Iterable[t.Callable[[], t.Awaitable[t.Any]]]) -> t.Callable[[], t.Awaitable[None]]:
    async def _close_wrapper() -> None:
        for cb in close_cbks:
            await cb()

    return _close_wrapper
