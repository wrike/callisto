from __future__ import annotations

import dataclasses as dc


@dc.dataclass(frozen=True)
class GraylogParameters:
    host: str
    port: int
