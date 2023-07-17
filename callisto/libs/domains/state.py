from __future__ import annotations

import dataclasses as dc
from enum import Enum


@dc.dataclass
class SessionState:
    patched_session_id: str
    browser_name: str
    test_name: str
    browser_version: str
    vnc_enabled: bool
    screen_resolution: str
    timezone: str


class SessionStage(Enum):
    CREATING = "creating"
    ACTIVE = "active"
    DELETING = "deleting"

    @classmethod
    def get_calc_duration_items(cls) -> list[SessionStage]:
        # TODO: calculate duration for `ACTIVE` stage
        return [cls.CREATING, cls.DELETING]


class SessionStageStep(Enum):
    # creating session
    CREATING_POD = "creating_pod"
    WAITING_FOR_POD_READY = "waiting_for_pod_ready"
    GETTING_POD = "getting_pod"
    CREATING_WEBDRIVER_SESSION = "creating_webdriver_session"

    # deleting session
    DELETING_POD = "deleting_pod"
