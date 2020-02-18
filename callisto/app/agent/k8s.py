from __future__ import annotations

from ...libs.domains.config import K8sConfig
from ...libs.services.k8s.client import K8sClient
from ...libs.services.k8s.service import K8sService
from ...libs.services.pod_event import PodEventService
from ...libs.services.task_runner import TaskRunnerService


async def init_k8s_service(k8s_config: K8sConfig, task_runner_service: TaskRunnerService) -> K8sService:
    k8s_client = await K8sClient.init(in_cluster=k8s_config.in_cluster, task_runner_service=task_runner_service)

    k8s_service = K8sService(k8s_client=k8s_client,
                             namespace=k8s_config.namespace,
                             pod_event_service=PodEventService(),
                             task_runner_service=task_runner_service)
    await k8s_service.run_background_tasks()
    return k8s_service
