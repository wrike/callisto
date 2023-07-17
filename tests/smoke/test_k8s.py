from __future__ import annotations

import asyncio

from async_timeout import timeout
from kubernetes_asyncio.client import V1PodList
from selenium.webdriver.remote.webdriver import WebDriver

from . import K8sAsync


async def browser_pod_exists(k8s: K8sAsync, pod_name: str) -> bool:
    pods: V1PodList = await k8s.v1_client.list_namespaced_pod(namespace="default")

    for pod in pods.items:
        if pod.metadata.name == pod_name:
            return True

    return False


async def test_pod_is_deleted(chrome_webdriver: WebDriver, k8s: K8sAsync):
    patched_session_id = chrome_webdriver.session_id
    pod_name = "-".join(patched_session_id.split("-")[:2])

    # check pod created
    assert await browser_pod_exists(k8s, pod_name) is True

    # close session
    chrome_webdriver.quit()

    # waiting for pod deletion
    async with timeout(30):
        while await browser_pod_exists(k8s, pod_name) is True:
            await asyncio.sleep(5)
