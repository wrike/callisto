from __future__ import annotations

from aiojobs import Scheduler


def init_scheduler() -> Scheduler:
    return Scheduler()
