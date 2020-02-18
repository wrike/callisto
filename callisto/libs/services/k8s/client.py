from __future__ import annotations

import typing as t

from aiohttp import (
    ClientConnectorError,
    ClientResponse,
    StreamReader,
)
from kubernetes_asyncio import (  # type: ignore
    client,
    config,
    watch,
)
from kubernetes_asyncio.client.rest import ApiException  # type: ignore

from ...exceptions import K8SForbidden, K8sPodNotFound
from ..log import l_ctx, logger
from ..task_runner import TaskRunnerService


if t.TYPE_CHECKING:
    from kubernetes_asyncio.client import (  # type: ignore
        V1APIVersions,
        V1Pod,
        CoreApi,
        CoreV1Api,
        V1Status,
    )

ReplicasCount = t.Dict[str, int]
T = t.TypeVar('T')


LISTENING_EVENT_TYPE = 'MODIFIED'
ERROR_EVENT_TYPE = 'ERROR'
SKIP_EVENT_TYPES = ('ADDED', 'DELETED')


class K8sClient:
    RUNNING_PHASE_NAME = 'Running'
    READY_CONDITION_TYPE = 'Ready'
    CONDITION_STATUS_OK = 'True'

    def __init__(self,
                 core_client: CoreApi,
                 v1_client: CoreV1Api,
                 task_runner_service: TaskRunnerService) -> None:
        self.core_client = core_client
        self.v1_client = v1_client
        self.task_runner_service = task_runner_service

    @classmethod
    async def init(cls, in_cluster: bool, task_runner_service: TaskRunnerService) -> K8sClient:
        if in_cluster:
            # auth inside k8s cluster
            config.load_incluster_config()
            configuration = client.Configuration()
        else:
            # local auth (from kubectl config)
            configuration = client.Configuration()
            await config.load_kube_config(client_configuration=configuration)

        api_client = client.ApiClient(configuration)
        core_client = client.CoreApi(api_client)
        v1_client = client.CoreV1Api(api_client)

        return cls(core_client=core_client, v1_client=v1_client, task_runner_service=task_runner_service)

    async def _retry(self,
                     *,
                     func: t.Callable[..., t.Any],
                     **kwargs: t.Any) -> t.Any:
        """Retry on:
            ClientConnectorError - when kube-api unavailable
            ApiException - some random errors
        """
        return await self.task_runner_service.run_with_retry(func=func,
                                                             tries=8,
                                                             pause=15,
                                                             retry_exc=(ClientConnectorError, ApiException),
                                                             **kwargs)

    async def get_api_versions(self) -> V1APIVersions:
        return await self.core_client.get_api_versions()

    async def get_pod(self, namespace: str, name: str) -> V1Pod:
        try:
            return await self._retry(func=self.v1_client.read_namespaced_pod, name=name, namespace=namespace)
        except ApiException as e:
            if e.status == 404:
                raise K8sPodNotFound(f'Pod `{name}` in namespace `{namespace}` not found') from e
            raise e

    async def create_pod(self, namespace: str, spec: t.Dict[str, t.Any]) -> V1Pod:
        try:
            return await self._retry(func=self.v1_client.create_namespaced_pod, namespace=namespace, body=spec)
        except ApiException as e:
            if e.status == 403:
                raise K8SForbidden(f"Can't create pod in namespace {namespace}. Pod manifest: {spec}") from e
            raise e

    async def delete_pod(self, namespace: str, name: str) -> V1Status:
        try:
            return await self._retry(func=self.v1_client.delete_namespaced_pod, namespace=namespace, name=name)
        except ApiException as e:
            if e.status == 403:
                raise K8SForbidden(f"Can't delete pod {name} in namespace {namespace}") from e
            if e.status == 404:
                raise K8sPodNotFound(f'Pod `{name}` in namespace `{namespace}` not found') from e
            raise e

    def is_pod_ready(self, pod: V1Pod) -> bool:
        if pod.status.phase == self.RUNNING_PHASE_NAME:
            for condition in pod.status.conditions:
                if condition.type == self.READY_CONDITION_TYPE and condition.status == self.CONDITION_STATUS_OK:
                    return True

        return False

    async def watch_pod_ready_events(self, namespace: str) -> t.AsyncIterator[str]:
        while True:
            async for event in watch.Watch().stream(
                    self.v1_client.list_namespaced_pod,
                    namespace=namespace,
            ):
                if event['type'] == LISTENING_EVENT_TYPE:
                    if self.is_pod_ready(event['object']):
                        pod_name = event['object'].metadata.name
                        logger.debug(f'pod is ready', extra=l_ctx(namespace=namespace, pod=pod_name))
                        yield pod_name
                elif event['type'] in SKIP_EVENT_TYPES:
                    pass
                elif event['type'] == ERROR_EVENT_TYPE and event['object'].get('code') == 410:
                    # clients must handle the case by recognizing the status code 410 Gone,
                    # clearing their local cache, performing a list operation,
                    # and starting the watch from the resourceVersion returned by that new list operation
                    # (see https://kubernetes.io/docs/reference/using-api/api-concepts/#efficient-detection-of-changes)
                    # TODO: handle resource_version after https://github.com/tomplus/kubernetes_asyncio/issues/77
                    break
                else:
                    logger.warning('unhandled event', extra=l_ctx(event=event))

    async def get_pod_logs_stream(self, namespace: str, name: str) -> StreamReader:
        resp: ClientResponse = await self.v1_client.read_namespaced_pod_log(name=name,
                                                                            namespace=namespace,
                                                                            follow=True,
                                                                            _preload_content=False)
        return resp.content
