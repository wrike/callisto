from __future__ import annotations

from aiohttp import web


async def test_health_check(run_test_server, aiohttp_test_client):
    app, server = await run_test_server()
    client = aiohttp_test_client(server)

    resp = await client.get("/health")

    assert resp.status == web.HTTPOk.status_code
