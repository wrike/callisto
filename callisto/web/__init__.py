from __future__ import annotations

from aiohttp.web import Request

from ..libs.exceptions import ValidationError


def get_pod_name(request: Request) -> str:
    try:
        return request.match_info['pod_name']
    except KeyError:
        raise ValidationError('No pod_name set')
