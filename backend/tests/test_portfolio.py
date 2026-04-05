# pyright: reportMissingImports=false, reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_empty_portfolio_returns_zeros(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/portfolio/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["totalPortfolioValue"] == 0.0
    assert data["dayPnl"] == 0.0
    assert data["openOrdersCount"] == 0


async def test_portfolio_always_paper_mode(async_client: AsyncClient) -> None:
    """Until real broker keys are wired, isPaperMode must always be True."""
    response = await async_client.get("/api/v1/portfolio/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["isPaperMode"] is True
