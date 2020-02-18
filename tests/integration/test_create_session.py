from __future__ import annotations

from asyncio import CancelledError
from unittest import mock

import pytest
from aiohttp import web
from kubernetes_asyncio.client.rest import ApiException

from callisto.libs.domains import consts
from callisto.libs.exceptions import WebDriverException


@pytest.mark.asyncio
async def test_create_session(future, run_test_server, aiohttp_test_client, k8s_pod, session_created_response):
    app, server = await run_test_server()
    client = aiohttp_test_client(server)
    webdriver_request = {"desiredCapabilities": {"browserName": "chrome"}}

    app[consts.SESSION_USE_CASE_KEY].k8s_service.create_pod = mock.Mock(return_value=future(k8s_pod()))
    app[consts.SESSION_USE_CASE_KEY].k8s_service.wait_until_pod_is_ready = mock.Mock(return_value=future())
    app[consts.SESSION_USE_CASE_KEY].k8s_service.get_pod = mock.Mock(return_value=future(k8s_pod()))
    app[consts.SESSION_USE_CASE_KEY].webdriver_service.create_session = mock.Mock(return_value=future(
        session_created_response
    ))

    resp = await client.post(f'/api/v1/session', json=webdriver_request)

    assert resp.status == web.HTTPOk.status_code
    assert len(app[consts.SESSION_USE_CASE_KEY].state_service.sessions) == 1
    app[consts.SESSION_USE_CASE_KEY].k8s_service.create_pod.assert_called_once()
    app[consts.SESSION_USE_CASE_KEY].k8s_service.wait_until_pod_is_ready.assert_called_once()
    app[consts.SESSION_USE_CASE_KEY].k8s_service.get_pod.assert_called_once()
    app[consts.SESSION_USE_CASE_KEY].webdriver_service.create_session.assert_called_once()


@pytest.mark.asyncio
async def test_return_error_on_error_during_pod_creation(run_test_server, aiohttp_test_client):
    app, server = await run_test_server()
    client = aiohttp_test_client(server)
    webdriver_request = {"desiredCapabilities": {"browserName": "chrome"}}

    app[consts.SESSION_USE_CASE_KEY].k8s_service.create_pod = mock.Mock(side_effect=ApiException())

    resp = await client.post(f'/api/v1/session', json=webdriver_request)

    assert resp.status == web.HTTPInternalServerError.status_code
    assert len(app[consts.SESSION_USE_CASE_KEY].state_service.sessions) == 0
    app[consts.SESSION_USE_CASE_KEY].k8s_service.create_pod.assert_called_once()


@pytest.mark.asyncio
async def test_delete_pod_on_cancelled_error_during_waiting_pod_ready(future,
                                                                      run_test_server,
                                                                      aiohttp_test_client,
                                                                      k8s_pod):
    app, server = await run_test_server()
    client = aiohttp_test_client(server)
    webdriver_request = {"desiredCapabilities": {"browserName": "chrome"}}

    app[consts.SESSION_USE_CASE_KEY].k8s_service.create_pod = mock.Mock(return_value=future(k8s_pod()))
    app[consts.SESSION_USE_CASE_KEY].k8s_service.wait_until_pod_is_ready = mock.Mock(side_effect=CancelledError())
    app[consts.SESSION_USE_CASE_KEY].k8s_service.delete_pod = mock.Mock(return_value=future())

    resp = await client.post(f'/api/v1/session', json=webdriver_request)

    assert resp.status == web.HTTPInternalServerError.status_code
    assert len(app[consts.SESSION_USE_CASE_KEY].state_service.sessions) == 0
    app[consts.SESSION_USE_CASE_KEY].k8s_service.delete_pod.assert_called_once()


@pytest.mark.asyncio
async def test_delete_pod_on_error_during_creation_webdriver_session(future,
                                                                     run_test_server,
                                                                     aiohttp_test_client,
                                                                     k8s_pod):
    app, server = await run_test_server()
    client = aiohttp_test_client(server)
    webdriver_request = {"desiredCapabilities": {"browserName": "chrome"}}

    app[consts.SESSION_USE_CASE_KEY].k8s_service.create_pod = mock.Mock(return_value=future(k8s_pod()))
    app[consts.SESSION_USE_CASE_KEY].k8s_service.wait_until_pod_is_ready = mock.Mock(return_value=future())
    app[consts.SESSION_USE_CASE_KEY].k8s_service.get_pod = mock.Mock(return_value=future(k8s_pod()))
    app[consts.SESSION_USE_CASE_KEY].webdriver_service.create_session = mock.Mock(side_effect=WebDriverException())
    app[consts.SESSION_USE_CASE_KEY].k8s_service.delete_pod = mock.Mock(return_value=future())

    resp = await client.post(f'/api/v1/session', json=webdriver_request)

    assert resp.status == web.HTTPInternalServerError.status_code
    assert len(app[consts.SESSION_USE_CASE_KEY].state_service.sessions) == 0
    app[consts.SESSION_USE_CASE_KEY].k8s_service.delete_pod.assert_called_once()
