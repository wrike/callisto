from __future__ import annotations

from unittest import mock

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient as AiohttpTestClient
from aiohttp.test_utils import TestServer

from callisto.app.agent.state import init_state_service
from callisto.app.agent.webdriver import init_webdriver_service
from callisto.libs.domains import consts
from callisto.libs.domains.config import K8sConfig, PodConfig
from callisto.libs.middleware import error_middleware, tracing_middleware_factory
from callisto.libs.services.k8s.client import K8sClient
from callisto.libs.services.k8s.service import K8sService
from callisto.libs.services.pod_event import PodEventService
from callisto.libs.services.task_runner import TaskRunnerService
from callisto.libs.trace import request_then_uuid_factory, trace_id
from callisto.libs.use_cases.health_check import HealthCheckUseCase
from callisto.libs.use_cases.metrics import MetricsUseCase
from callisto.libs.use_cases.session import SessionUseCase
from callisto.libs.use_cases.status import StatusUseCase
from callisto.libs.use_cases.webdriver_logs import WebdriverLogsUseCase
from callisto.web.routes import setup_routes


async def _init_k8s_service(k8s_config: K8sConfig, task_runner_service: TaskRunnerService) -> K8sService:
    k8s_client = K8sClient(core_client=mock.Mock(), v1_client=mock.Mock(), task_runner_service=task_runner_service)

    k8s_service = K8sService(k8s_client=k8s_client,
                             namespace=k8s_config.namespace,
                             pod_event_service=PodEventService(),
                             task_runner_service=task_runner_service)
    return k8s_service


async def _init_task_runner_service() -> TaskRunnerService:
    async def spawn(coro):
        await coro
    scheduler = mock.Mock()
    scheduler.spawn = spawn

    return TaskRunnerService(scheduler=scheduler)


@pytest.fixture
def get_config():
    k8s_config = K8sConfig(in_cluster=True, namespace='default')
    pod_config = PodConfig(manifest={}, webdriver_path='', webdriver_port=4444)
    instance_id = 'unknown'
    graylog_config = None

    return k8s_config, pod_config, instance_id, graylog_config


@pytest.fixture
async def app_state(future, get_config):
    k8s_config, pod_config, instance_id, graylog_config = get_config

    task_runner_service = await _init_task_runner_service()
    k8s_service = await _init_k8s_service(k8s_config=k8s_config, task_runner_service=task_runner_service)
    state_service = init_state_service(k8s_service=k8s_service, instance_id=instance_id)

    webdriver_service = init_webdriver_service(task_runner_service, pod_config=pod_config)

    return {
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


@pytest.fixture
async def run_test_server(future, app_state):
    """
    Run API web application. Some services are replaced with simpler ones.
    """
    server = None

    async def wrapped():
        app = web.Application(middlewares=[tracing_middleware_factory(trace_id, request_then_uuid_factory()),
                                           error_middleware])

        app.update(app_state)
        setup_routes(app)

        nonlocal server
        server = TestServer(app)

        await server.start_server()

        return app, server

    yield wrapped

    await server.close()


@pytest.fixture
async def aiohttp_test_client():
    client = None

    def wrapped(app):
        nonlocal client
        client = AiohttpTestClient(app)
        return client

    yield wrapped

    await client.close()
