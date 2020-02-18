from __future__ import annotations

import typing as t
from asyncio import CancelledError

import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from ...libs.exceptions import K8SEmptyPodIp


if t.TYPE_CHECKING:
    from sentry_sdk._types import Event, Hint


def filter_exceptions(event: Event, hint: Hint) -> t.Optional[Event]:
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        # CanceledError may be too noisy. This is normal behavior when tests reset the connection
        # K8SEmptyPodIp occurs due to K8s errors, we can't do anything with it
        if exc_type in (CancelledError, K8SEmptyPodIp):
            return None
    return event


def init_sentry(sentry_dsn: str, instance_id: str) -> None:
    sentry_sdk.init(sentry_dsn, integrations=[AioHttpIntegration()], before_send=filter_exceptions)

    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("instance_id", instance_id)
