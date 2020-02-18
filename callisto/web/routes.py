from __future__ import annotations

import typing as t


if t.TYPE_CHECKING:
    from aiohttp.web import Application

API_PREFIX = '/api/v1'


def setup_routes(app: Application) -> None:
    from . import health_check
    from . import metrics
    from . import session
    from . import status
    from . import webdriver_logs

    app.router.add_get(f'/health', health_check.health_check_handler)
    app.router.add_get(f'/metrics', metrics.metrics_handler)
    app.router.add_get(f'{API_PREFIX}/status', status.status_handler)
    app.router.add_get(f'{API_PREFIX}/logs/{{pod_name}}', webdriver_logs.webdriver_logs_handler)
    app.router.add_post(f'{API_PREFIX}/session', session.create_session_handler)
    app.router.add_delete(f'{API_PREFIX}/session/{{pod_name}}', session.delete_session_handler)
