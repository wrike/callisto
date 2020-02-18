from __future__ import annotations

import asyncio
import typing as t


class PodEventService:
    def __init__(self) -> None:
        self.events: t.Dict[str, asyncio.Event] = {}

    def get_or_create_event(self, pod_name: str) -> asyncio.Event:
        if pod_name not in self.events:
            self.events[pod_name] = asyncio.Event()

        return self.events[pod_name]

    def clean(self, pod_name: str) -> None:
        del self.events[pod_name]
