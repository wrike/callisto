from __future__ import annotations

import asyncio

import pytest


pytest_plugins = (
    "integration.fixtures.k8s",
    "integration.fixtures.webdriver",
)


@pytest.fixture
def future():
    def wrapper(result=None):
        fut = asyncio.Future()
        fut.set_result(result)
        return fut

    return wrapper
