from __future__ import annotations

from aiojobs import Scheduler  # type: ignore

from ...libs.services.task_runner import TaskRunnerService


async def init_task_runner_service(scheduler: Scheduler) -> TaskRunnerService:
    return TaskRunnerService(scheduler=scheduler)
