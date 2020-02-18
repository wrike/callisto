from __future__ import annotations

from kubernetes_asyncio import client


class K8sAsync:
    def __init__(self, core_client: client.CoreApi, v1_client: client.CoreV1Api):
        self.core_client = core_client
        self.v1_client = v1_client
