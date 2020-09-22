from __future__ import annotations

import logging
import typing as t

import tenacity as tnc
from aiojobs import Scheduler  # type: ignore

from .log import logger


T = t.TypeVar('T')


class TaskRunnerService:
    def __init__(self, scheduler: Scheduler) -> None:
        self.scheduler = scheduler

    @staticmethod
    async def run_with_retry(func: t.Callable[..., t.Awaitable[T]],
                             tries: t.Optional[int] = 2,
                             pause: t.Optional[int] = 15,
                             retry_exc: t.Union[t.Type[Exception], t.Sequence[t.Type[Exception]]] = Exception,
                             *args: t.Any,
                             **kwargs: t.Any) -> T:

        return await tnc.AsyncRetrying(  # type: ignore
            wait=tnc.wait_fixed(pause),
            stop=tnc.stop_after_attempt(tries),
            retry=tnc.retry_if_exception_type(retry_exc),
            reraise=True,
            before=tnc.before_log(logger, logging.DEBUG),
            after=tnc.after_log(logger, logging.DEBUG),
            retry_error_cls=tnc.RetryError,
        ).call(func, *args, **kwargs)

    async def run_in_background(self, func: t.Callable[[], t.Awaitable[T]]) -> None:
        await self.scheduler.spawn(func())
