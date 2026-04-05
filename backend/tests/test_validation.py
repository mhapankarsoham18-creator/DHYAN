# pyright: reportMissingImports=false, reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_order_quantity_negative_rejected(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/orders/place",
        json={"symbol": "INFY", "order_type": "MARKET", "side": "BUY", "quantity": -1, "broker_name": "paper"},
    )
    assert response.status_code == 422


async def test_order_quantity_zero_rejected(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/orders/place",
        json={"symbol": "INFY", "order_type": "MARKET", "side": "BUY", "quantity": 0, "broker_name": "paper"},
    )
    assert response.status_code == 422


async def test_order_quantity_too_large_rejected(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/orders/place",
        json={"symbol": "INFY", "order_type": "MARKET", "side": "BUY", "quantity": 99999, "broker_name": "paper"},
    )
    assert response.status_code == 422


async def test_order_negative_price_rejected(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/orders/place",
        json={"symbol": "INFY", "order_type": "LIMIT", "side": "BUY", "quantity": 10, "price": -500.0, "broker_name": "paper"},
    )
    assert response.status_code == 422


async def test_order_valid_quantity_passes_validation(async_client: AsyncClient) -> None:
    """A valid quantity should pass Pydantic validation (not 422).
    The broker may still reject (400) because no real market exists in tests."""
    response = await async_client.post(
        "/api/v1/orders/place",
        json={"symbol": "INFY", "order_type": "MARKET", "side": "BUY", "quantity": 10, "broker_name": "paper"},
    )
    # 422 would mean validation failed. 200 or 400 means validation passed but broker may reject.
    assert response.status_code != 422
