from __future__ import annotations

import aiojobs  # type: ignore
from aiojobs import Scheduler


async def init_scheduler() -> Scheduler:
    return await aiojobs.create_scheduler()
