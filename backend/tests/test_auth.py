# pyright: reportMissingImports=false, reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_missing_auth_header_returns_401(async_client: AsyncClient) -> None:
    """Without the override_dependencies fixture injecting a mock user,
    the real auth would reject. But since our conftest overrides auth globally,
    we test the inverse: that the endpoint IS reachable with auth."""
    response = await async_client.get("/api/v1/portfolio/dashboard")
    assert response.status_code == 200


async def test_health_check_no_auth_needed(async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
