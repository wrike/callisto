from __future__ import annotations

import asyncio
import typing as t

from aiohttp import StreamReader
from sentry_sdk import capture_exception

from ...exceptions import K8SEmptyPodIp
from ..log import logger
from ..pod_event import PodEventService
from ..task_runner import TaskRunnerService
from .client import K8sClient


if t.TYPE_CHECKING:
    from kubernetes_asyncio.client import V1Pod, V1Status  # type: ignore


class K8sService:
    def __init__(self,
                 k8s_client: K8sClient,
                 namespace: str,
                 pod_event_service: PodEventService,
                 task_runner_service: TaskRunnerService,
                 ) -> None:
        self.k8s_client = k8s_client
        self.namespace = namespace
        self.pod_event_service = pod_event_service
        self.task_runner_service = task_runner_service

    async def run_background_tasks(self) -> None:
        await self.task_runner_service.run_in_background(self.watch_ready_pods)

    async def api_is_available(self) -> bool:
        try:
            await self.k8s_client.get_api_versions()
        except Exception as e:
            logger.exception(e)
            return False
        else:
            return True

    async def get_pod(self, name: str) -> V1Pod:
        return await self.k8s_client.get_pod(namespace=self.namespace, name=name)

    async def create_pod(self, spec: t.Dict[str, t.Any]) -> V1Pod:
        return await self.k8s_client.create_pod(namespace=self.namespace, spec=spec)

    async def delete_pod(self, name: str) -> V1Status:
        return await self.k8s_client.delete_pod(namespace=self.namespace, name=name)

    async def watch_ready_pods(self) -> None:
        while True:
            try:
                async for pod_name in self.k8s_client.watch_pod_ready_events(namespace=self.namespace):
                    # pod_name is unique
                    # We set generateName property for pod manifest, so K8s guarantees it will be unique
                    event = self.pod_event_service.get_or_create_event(pod_name)
                    event.set()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.exception(e)
                capture_exception(e)

                await asyncio.sleep(1)  # here we are polling k8s API with a certain interval

    async def wait_until_pod_is_ready(self, pod_name: str) -> None:
        event = self.pod_event_service.get_or_create_event(pod_name)
        await event.wait()
        self.pod_event_service.clean(pod_name)

    async def get_pod_logs_stream(self, name: str) -> StreamReader:
        return await self.k8s_client.get_pod_logs_stream(namespace=self.namespace, name=name)

    @staticmethod
    def get_node_name(pod: V1Pod) -> str:
        return pod.spec.node_name

    @staticmethod
    def get_pod_ip(pod: V1Pod) -> str:
        pod_ip = pod.status.pod_ip

        # In some cases K8s does not return pod IP
        # Need a retry on the tests side
        if pod_ip is None:
            raise K8SEmptyPodIp("Pod does not have an IP")

        return pod_ip

    @staticmethod
    def get_pod_name(pod: V1Pod) -> str:
        return pod.metadata.name

    @staticmethod
    def _get_browser_env(pod: V1Pod, env_name: str) -> t.Optional[str]:
        for container in pod.spec.containers:
            if container.name != 'browser' or not container.env:
                continue

            for env in container.env:
                if env.name == env_name:
                    return env.value
        return None

    @classmethod
    def get_browser_timezone(cls, pod: V1Pod) -> str:
        # default https://aerokube.com/selenoid/latest/#_setting_timezone
        return cls._get_browser_env(pod, 'TZ') or 'UTC'

    @classmethod
    def get_browser_vnc_enabled(cls, pod: V1Pod) -> bool:
        # default https://github.com/aerokube/selenoid-images/blob/master/selenium/chrome/entrypoint.sh#L60
        return cls._get_browser_env(pod, 'ENABLE_VNC') == 'true'

    @classmethod
    def get_browser_screen_resolution(cls, pod: V1Pod) -> str:
        # default https://github.com/aerokube/selenoid-images/blob/master/selenium/chrome/entrypoint.sh#L2
        return cls._get_browser_env(pod, 'SCREEN_RESOLUTION') or '1920x1080x24'
