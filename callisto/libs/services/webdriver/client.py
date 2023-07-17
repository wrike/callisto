from __future__ import annotations

import typing as t
from json import JSONDecodeError

from aiohttp import ClientSession

from ...exceptions import WebDriverException


class WebDriverClient:
    ALLOWED_CODES = (200,)

    async def request(self, url: str, method: str, json: dict[str, t.Any]) -> dict[str, t.Any]:
        async with ClientSession() as session:
            async with session.request(method=method, url=url, json=json) as response:
                if response.status not in self.ALLOWED_CODES:
                    raise WebDriverException(f"Url {url} returned {response.status} status code")
                try:
                    return await response.json()
                except JSONDecodeError:
                    raise WebDriverException(f"Can't parse response for url {url}")
