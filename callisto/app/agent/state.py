from __future__ import annotations

from ...libs.services.k8s.service import K8sService
from ...libs.services.state import StateService


def init_state_service(k8s_service: K8sService, instance_id: str) -> StateService:
    return StateService(k8s_service=k8s_service, instance_id=instance_id)
