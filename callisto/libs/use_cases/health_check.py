from __future__ import annotations


class HealthCheckUseCase:
    async def is_healthy(self) -> bool:
        return True
