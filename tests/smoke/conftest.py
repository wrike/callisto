from __future__ import annotations

import asyncio

import pytest
from kubernetes_asyncio import client, config
from selenium import webdriver
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.remote.webdriver import WebDriver

from . import K8sAsync


def pytest_addoption(parser):
    parser.addoption("--callisto-endpoint", action="store")


@pytest.fixture()
def callisto_endpoint(pytestconfig):
    return pytestconfig.getoption("callisto_endpoint")


# overwrite event_loop fixture for extending scope to session (otherwise k8s fixture will not work)
# see https://github.com/pytest-dev/pytest-asyncio/issues/68#issuecomment-334083751 for details
@pytest.yield_fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def chrome_webdriver(callisto_endpoint) -> WebDriver:
    capabilities = {
        "browserName": "chrome",
        "goog:chromeOptions": {
            "args": ["--no-sandbox"]  # chrome crashes in kind without this option
        }
    }

    chrome_webdriver = webdriver.Remote(
        command_executor=RemoteConnection(callisto_endpoint, resolve_ip=False),
        desired_capabilities=capabilities,
    )

    yield chrome_webdriver

    chrome_webdriver.quit()


@pytest.fixture(scope='session')
async def k8s() -> K8sAsync:
    configuration = client.Configuration()
    await config.load_kube_config(client_configuration=configuration)
    api_client = client.ApiClient(configuration)

    return K8sAsync(core_client=client.CoreApi(api_client), v1_client=client.CoreV1Api(api_client))
