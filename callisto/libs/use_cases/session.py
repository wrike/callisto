from __future__ import annotations

import typing as t
from concurrent.futures import CancelledError

from sentry_sdk import capture_exception

from ..domains.state import SessionStage, SessionStageStep
from ..exceptions import (
    K8sPodNotFound,
    SessionNotFound,
    WebDriverException,
)
from ..helpers import async_partial
from ..services.log import l_ctx, logger
from ..services.state import record_stage_stats, record_step_stats
from ..services.webdriver.protocol import WebDriverProtocol


if t.TYPE_CHECKING:
    from ..domains.config import PodConfig
    from ..services.k8s.service import K8sService
    from ..services.state import StateService
    from ..services.task_runner import TaskRunnerService
    from ..services.webdriver.service import WebDriverService


class SessionUseCase:
    def __init__(self,
                 k8s_service: K8sService,
                 webdriver_service: WebDriverService,
                 pod_config: PodConfig,
                 state_service: StateService,
                 task_runner_service: TaskRunnerService,
                 ) -> None:
        self.k8s_service = k8s_service
        self.webdriver_service = webdriver_service
        self.pod_config = pod_config
        self.state_service = state_service
        self.task_runner_service = task_runner_service

    async def create_session(self, session_request: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        with record_stage_stats(self.state_service, SessionStage.CREATING):
            pod_name = await self._run_pod()
            with record_step_stats(self.state_service, SessionStageStep.GETTING_POD):
                pod = await self.k8s_service.get_pod(pod_name)
            pod_ip = self.k8s_service.get_pod_ip(pod)

            session_response = await self._create_session(session_request=session_request,
                                                          pod_name=pod_name,
                                                          pod_ip=pod_ip)
            logger.info('session created', extra=l_ctx(session_id=WebDriverProtocol.get_session_id(session_response),
                                                       pod=pod_name,
                                                       pod_ip=pod_ip,
                                                       node_name=self.k8s_service.get_node_name(pod)))

            patched_session_response = WebDriverProtocol.patch_session_response(session_response=session_response,
                                                                                pod_name=pod_name,
                                                                                pod_ip=pod_ip)
            self.state_service.add_session(pod=pod,
                                           session_request=session_request,
                                           patched_session_response=patched_session_response)
            return patched_session_response

    async def delete_session(self, pod_name: str) -> t.Dict[str, t.Any]:
        await self.task_runner_service.run_in_background(
            async_partial(self._delete_session, pod_name=pod_name))

        # Always return the correct answer to client.
        # Cleanup errors shouldn't affect the tests results.
        return WebDriverProtocol.get_session_deleted_response()

    async def _delete_session(self, pod_name: str) -> None:
        try:
            with record_stage_stats(self.state_service, SessionStage.DELETING):
                with record_step_stats(self.state_service, SessionStageStep.DELETING_POD):
                    await self._delete_pod(name=pod_name)
                logger.info('session deleted', extra=l_ctx(pod=pod_name))
        except K8sPodNotFound as e:
            # It looks like pod was preempted.
            # This is normal behavior for preemptible nodes.
            logger.warning(e)
        except Exception as e:
            logger.exception(e)
            capture_exception(e)
        finally:
            try:
                self.state_service.remove_session(pod_name=pod_name)
            except SessionNotFound as e:
                logger.warning(e)

    async def _run_pod(self) -> str:
        logger.debug('creating pod')
        with record_step_stats(self.state_service, SessionStageStep.CREATING_POD):
            pod = await self.k8s_service.create_pod(spec=self.pod_config.manifest)
        pod_name = self.k8s_service.get_pod_name(pod)
        logger.debug('pod created', extra=l_ctx(pod=pod_name))

        try:
            with record_step_stats(self.state_service, SessionStageStep.WAITING_FOR_POD_READY):
                await self.k8s_service.wait_until_pod_is_ready(pod_name=pod_name)
        except CancelledError as e:
            await self._delete_pod(name=pod_name)
            raise e

        return pod_name

    async def _create_session(self,
                              session_request: t.Dict[str, t.Any],
                              pod_name: str,
                              pod_ip: str,
                              ) -> t.Dict[str, t.Any]:
        try:
            with record_step_stats(self.state_service, SessionStageStep.CREATING_WEBDRIVER_SESSION):
                session_response = await self.webdriver_service.create_session(pod_ip=pod_ip,
                                                                               session_request=session_request)
            logger.debug('webdriver session created',
                         extra=l_ctx(pod=pod_name, session_id=WebDriverProtocol.get_session_id(session_response)))
        except (CancelledError, WebDriverException) as e:
            await self._delete_pod(name=pod_name)
            raise e

        if not WebDriverProtocol.is_session_created(session_response):
            await self._delete_pod(name=pod_name)
            raise WebDriverException(f'Create session error: {session_response}')

        return session_response

    async def _delete_pod(self, name: str) -> None:
        logger.debug('deleting pod', extra=l_ctx(pod=name))
        await self.k8s_service.delete_pod(name=name)
