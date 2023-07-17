from __future__ import annotations

from textwrap import dedent

from aiohttp import web


async def test_metrics(run_test_server, aiohttp_test_client):
    app, server = await run_test_server()
    client = aiohttp_test_client(server)
    expected = dedent(
        """
        # HELP callisto_k8s_api_available Availability of K8s api
        # TYPE callisto_k8s_api_available gauge
        callisto_k8s_api_available{instance_id="unknown"} 0.0
        # HELP callisto_inprocessing_sessions Sessions now in progress
        # TYPE callisto_inprocessing_sessions gauge
        callisto_inprocessing_sessions{instance_id="unknown",stage="active"} 0.0
        # HELP callisto_processed_sessions_total Total processed sessions
        # TYPE callisto_processed_sessions_total counter
        # HELP callisto_processed_steps_total Total processed steps
        # TYPE callisto_processed_steps_total counter
        # HELP callisto_sessions_duration Stages duration
        # TYPE callisto_sessions_duration histogram
        # HELP callisto_stage_steps_duration Steps duration
        # TYPE callisto_stage_steps_duration histogram
    """
    ).lstrip()

    resp = await client.get("/metrics")
    text = await resp.text()

    assert resp.status == web.HTTPOk.status_code
    assert text == expected
