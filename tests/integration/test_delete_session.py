from __future__ import annotations

from unittest import mock

import pytest
from aiohttp import web

from callisto.libs.domains import consts
from callisto.libs.exceptions import K8sPodNotFound


@pytest.mark.asyncio
async def test_delete_session(future, run_test_server, aiohttp_test_client):
    app, server = await run_test_server()
    client = aiohttp_test_client(server)
    pod_name = 'browser-xtc9s'

    app[consts.SESSION_USE_CASE_KEY].k8s_service.delete_pod = mock.Mock(return_value=future())

    resp = await client.delete(f'/api/v1/session/{pod_name}')

    assert resp.status == web.HTTPOk.status_code
    app[consts.SESSION_USE_CASE_KEY].k8s_service.delete_pod.assert_called_once_with(name=pod_name)


@pytest.mark.asyncio
async def test_return_httpok_on_deletion_error(run_test_server, aiohttp_test_client):
    app, server = await run_test_server()
    client = aiohttp_test_client(server)
    pod_name = 'browser-xtc9s'

    app[consts.SESSION_USE_CASE_KEY].k8s_service.delete_pod = mock.Mock(side_effect=K8sPodNotFound())

    resp = await client.delete(f'/api/v1/session/{pod_name}')

    assert resp.status == web.HTTPOk.status_code
    app[consts.SESSION_USE_CASE_KEY].k8s_service.delete_pod.assert_called_once_with(name=pod_name)
