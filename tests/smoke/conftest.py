from __future__ import annotations

import pytest
from kubernetes_asyncio import client, config
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from . import K8sAsync


def pytest_addoption(parser):
    parser.addoption("--callisto-endpoint", action="store")


@pytest.fixture()
def callisto_endpoint(pytestconfig):
    return pytestconfig.getoption("callisto_endpoint")


@pytest.fixture
def chrome_webdriver(callisto_endpoint) -> WebDriver:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")  # chrome crashes in kind without this option

    chrome_webdriver = webdriver.Remote(
        command_executor=callisto_endpoint,
        options=chrome_options,
    )

    yield chrome_webdriver

    chrome_webdriver.quit()


@pytest.fixture
async def k8s() -> K8sAsync:
    await config.load_kube_config()
    api_client = client.ApiClient()

    return K8sAsync(core_client=client.CoreApi(api_client), v1_client=client.CoreV1Api(api_client))
