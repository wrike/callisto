from __future__ import annotations

from aiohttp import web

from ..use_cases.health_check import HealthCheckUseCase
from ..use_cases.metrics import MetricsUseCase
from ..use_cases.session import SessionUseCase
from ..use_cases.status import StatusUseCase
from ..use_cases.webdriver_logs import WebdriverLogsUseCase


HEALTH_CHECK_USE_CASE_KEY = web.AppKey("__health_check_use_case_key__", HealthCheckUseCase)
METRICS_USE_CASE_KEY = web.AppKey("__metrics_use_case_key__", MetricsUseCase)
SESSION_USE_CASE_KEY = web.AppKey("__session_use_case_key__", SessionUseCase)
STATUS_USE_CASE_KEY = web.AppKey("__status_use_case_key__", StatusUseCase)
WEBDRIVER_LOGS_USE_CASE_KEY = web.AppKey("__webdriver_logs_use_case_key__", WebdriverLogsUseCase)
