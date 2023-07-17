from __future__ import annotations

import logging
import logging.config
import typing as t

from ...libs.domains.logging import GraylogParameters
from ...libs.services.log import get_logger


logger = get_logger("callisto.agent")


class AddInstanceIdFilter(logging.Filter):
    def __init__(self, name: str = "", *, instance_id: str):
        super().__init__(name=name)
        self.instance_id = instance_id

    def filter(self, record: logging.LogRecord) -> bool:
        record.instance_id = self.instance_id
        return True


def get_default_logging_config(instance_id: str, graylog_config: GraylogParameters | None = None) -> dict[str, t.Any]:
    handlers_seq = ["console"]
    handlers: dict[str, t.Any] = {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "simpleFormatter",
            "level": "NOTSET",
        }
    }

    if graylog_config is not None:
        handlers["graypy"] = {
            "class": "graypy.GELFUDPHandler",
            "host": graylog_config.host,
            "port": graylog_config.port,
            "formatter": "simpleFormatter",
            "level": "NOTSET",
            "filters": ["add_instance_id"],
        }
        handlers_seq.append("graypy")

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "level": "NOTSET",
            "handlers": handlers_seq,
        },
        "handlers": handlers,
        "filters": {
            "add_instance_id": {
                "()": lambda: AddInstanceIdFilter(instance_id=instance_id),
            },
        },
        "formatters": {
            "simpleFormatter": {
                "class": "logging.Formatter",
                # instance_id - Unique ID for this callisto instance
                "format": f"%(asctime)s {instance_id} %(levelname)s %(message)s",
            }
        },
    }


def init_logger(*, config: dict[str, t.Any], log_level: int) -> None:
    logging.config.dictConfig(config)
    root = logging.getLogger()
    root.setLevel(log_level)

    root.info("init logger")
