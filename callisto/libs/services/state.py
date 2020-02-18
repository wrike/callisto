from __future__ import annotations

import dataclasses as dc
import typing as t
from contextlib import contextmanager
from datetime import datetime

from kubernetes_asyncio.client import V1Pod  # type: ignore
from prometheus_client import (  # type: ignore
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from ..domains.state import (
    SessionStage,
    SessionStageStep,
    SessionState,
)
from ..exceptions import SessionNotFound
from .k8s.service import K8sService
from .webdriver.protocol import WebDriverProtocol


@dc.dataclass(frozen=True)
class TimeMeasurement:
    succeeded: bool
    duration: float


@contextmanager
def record_stage_stats(state_service: StateService, stage: SessionStage) -> t.Iterator[None]:
    start_time = datetime.utcnow()
    state_service.stages_processing.labels(instance_id=state_service.instance_id,
                                           stage=stage.value).inc()
    try:
        yield

        state_service.stages_processed.labels(instance_id=state_service.instance_id,
                                              stage=stage.value,
                                              succeeded=True).inc()
        state_service.stages_duration.labels(instance_id=state_service.instance_id,
                                             stage=stage.value,
                                             succeeded=True).observe((datetime.utcnow() - start_time).total_seconds())
    except Exception:
        state_service.stages_processed.labels(instance_id=state_service.instance_id,
                                              stage=stage.value,
                                              succeeded=False).inc()
        state_service.stages_duration.labels(instance_id=state_service.instance_id,
                                             stage=stage.value,
                                             succeeded=False).observe((datetime.utcnow() - start_time).total_seconds())
        raise
    finally:
        state_service.stages_processing.labels(instance_id=state_service.instance_id,
                                               stage=stage.value).dec()


@contextmanager
def record_step_stats(state_service: StateService, step: SessionStageStep) -> t.Iterator[None]:
    start_time = datetime.utcnow()

    try:
        yield

        state_service.stage_steps_processed.labels(instance_id=state_service.instance_id,
                                                   step=step.value,
                                                   succeeded=True).inc()
        state_service.stage_steps_duration.labels(instance_id=state_service.instance_id,
                                                  step=step.value,
                                                  succeeded=True,
                                                  ).observe((datetime.utcnow() - start_time).total_seconds())
    except Exception:
        state_service.stage_steps_processed.labels(instance_id=state_service.instance_id,
                                                   step=step.value,
                                                   succeeded=False).inc()
        state_service.stage_steps_duration.labels(instance_id=state_service.instance_id,
                                                  step=step.value,
                                                  succeeded=False,
                                                  ).observe((datetime.utcnow() - start_time).total_seconds())
        raise


class StateService:
    DEFAULT_BUCKETS = (0.1, 0.25, 0.5, 1, 5, 10, 15, 30, 45, 60, 90, 120, 240)

    def __init__(self,
                 k8s_service: K8sService,
                 instance_id: str,
                 ) -> None:
        self.metrics_registry = CollectorRegistry(auto_describe=True)
        self.k8s_service = k8s_service
        self.instance_id = instance_id
        self.sessions: t.Dict[str, SessionState] = {}

        self.k8s_api_available = Gauge(
            'callisto_k8s_api_available',
            'Availability of K8s api',
            ['instance_id'],
            registry=self.metrics_registry,
        )
        self.stages_processing = Gauge(
            'callisto_inprocessing_sessions',
            'Sessions now in progress',
            ['instance_id', 'stage'],
            registry=self.metrics_registry,
        )
        self.stages_processed = Counter(
            'callisto_processed_sessions_total',
            'Total processed sessions',
            ['instance_id', 'stage', 'succeeded'],
            registry=self.metrics_registry,
        )
        self.stage_steps_processed = Counter(
            'callisto_processed_steps_total',
            'Total processed steps',
            ['instance_id', 'step', 'succeeded'],
            registry=self.metrics_registry,
        )
        self.stages_duration = Histogram(
            'callisto_sessions_duration',
            'Stages duration',
            ['instance_id', 'stage', 'succeeded'],
            buckets=self.DEFAULT_BUCKETS,
            registry=self.metrics_registry,
        )
        self.stage_steps_duration = Histogram(
            'callisto_stage_steps_duration',
            'Steps duration',
            ['instance_id', 'step', 'succeeded'],
            buckets=self.DEFAULT_BUCKETS,
            registry=self.metrics_registry,
        )

    def add_session(self,
                    pod: V1Pod,
                    session_request: t.Dict[str, t.Any],
                    patched_session_response: t.Dict[str, t.Any],
                    ) -> None:
        patched_session_id = WebDriverProtocol.get_session_id(patched_session_response)
        browser_name = WebDriverProtocol.get_browser_name(patched_session_response)
        test_name = WebDriverProtocol.get_test_name(session_request)
        browser_version = WebDriverProtocol.get_browser_version(patched_session_response)
        pod_name = self.k8s_service.get_pod_name(pod)
        timezone = self.k8s_service.get_browser_timezone(pod)
        vnc_enabled = self.k8s_service.get_browser_vnc_enabled(pod)
        screen_resolution = self.k8s_service.get_browser_screen_resolution(pod)

        self.sessions[pod_name] = SessionState(patched_session_id=patched_session_id,
                                               browser_name=browser_name,
                                               test_name=test_name,
                                               browser_version=browser_version,
                                               timezone=timezone,
                                               vnc_enabled=vnc_enabled,
                                               screen_resolution=screen_resolution)

    def remove_session(self, pod_name: str) -> None:
        try:
            del self.sessions[pod_name]
        except KeyError:
            raise SessionNotFound(f'Session for pod {pod_name} not found')

    def get_active_sessions(self) -> t.Dict[str, SessionState]:
        return self.sessions

    def get_active_sessions_number(self) -> int:
        return len(self.sessions)

    def get_sessions_creating(self) -> int:
        return self.stages_processing.labels(instance_id=self.instance_id,
                                             stage=SessionStage.CREATING.value)._value.get()

    def _update_active_sessions(self) -> None:
        metric = self.stages_processing.labels(
            instance_id=self.instance_id,
            stage=SessionStage.ACTIVE.value
        )

        metric.set(self.get_active_sessions_number())

    async def collect_metrics(self) -> str:
        self.k8s_api_available.labels(instance_id=self.instance_id).set(int(await self.k8s_service.api_is_available()))
        self._update_active_sessions()

        return generate_latest(self.metrics_registry)
