from __future__ import annotations

import asyncio
import logging
import logging.config
import typing as t

from ...libs.domains.logging import GraylogParameters
from .logger import logger
from .runner import run_agent


if t.TYPE_CHECKING:
    from ...libs.domains.config import (
        K8sConfig,
        PodConfig,
        WebOptions,
    )


def main(web_parameters: WebOptions,
         log_level_name: str,
         k8s_config: K8sConfig,
         pod_config: PodConfig,
         instance_id: str,
         sentry_dsn: str,
         graylog_config: t.Optional[GraylogParameters]
         ) -> None:
    try:
        log_level = int(logging.getLevelName(log_level_name))
    except ValueError as e:
        raise RuntimeError(f"Incorrect log level {log_level_name}") from e

    loop = asyncio.get_event_loop()
    close_callback = loop.run_until_complete(run_agent(
        web_parameters=web_parameters,
        log_level=log_level,
        k8s_config=k8s_config,
        pod_config=pod_config,
        instance_id=instance_id,
        sentry_dsn=sentry_dsn,
        graylog_config=graylog_config,
    ))

    try:
        logger.info('run loop')

        loop.run_forever()
    finally:
        loop.run_until_complete(close_callback())
        loop.close()
