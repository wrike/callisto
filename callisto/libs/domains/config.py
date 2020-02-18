from __future__ import annotations

import dataclasses as dc
import typing as t


@dc.dataclass(frozen=True)
class WebOptions:
    host: str
    port: int


@dc.dataclass(frozen=True)
class K8sConfig:
    in_cluster: bool
    namespace: str


@dc.dataclass(frozen=True)
class PodConfig:
    manifest: t.Dict[str, t.Any]
    webdriver_path: str
    webdriver_port: int
