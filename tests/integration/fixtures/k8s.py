from __future__ import annotations

import os
from unittest import mock

import pytest
from kubernetes_asyncio.client import ApiClient, V1Pod


@pytest.fixture()
def k8s_pod():
    def make_pod(pod_name: str = "browser-xtc9s") -> V1Pod:
        resp = mock.Mock()

        with open(os.path.join(os.path.dirname(__file__), "pod_fixture.json")) as data:
            resp.data = data.read().replace("{pod_name}", pod_name)

        return ApiClient().deserialize(resp, "V1Pod")

    return make_pod
