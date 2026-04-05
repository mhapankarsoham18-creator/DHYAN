# pyright: reportMissingImports=false, reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnusedParameter=false, reportMissingParameterType=false, reportUnknownParameterType=false

import pytest
from typing import Any
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, MagicMock

pytestmark = pytest.mark.asyncio

async def test_place_paper_order_success(async_client: AsyncClient, mock_db_session: MagicMock) -> None:
    # Call order endpoint
    response = await async_client.post(
        "/api/v1/orders/place",
        json={
            "symbol": "RELIANCE",
            "order_type": "LIMIT",
            "side": "BUY",
            "quantity": 10,
            "price": 2500.0,
            "broker_name": "paper"
        }
    )
    
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["status"] == "success"
    assert data["broker"] == "paper"
    
    # Assert DB add & commit was called
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_awaited()

@patch('app.routes.orders.create_broker_client')
async def test_place_live_order_broker_rejected(mock_create_broker_client: Any, async_client: AsyncClient, mock_db_session: MagicMock) -> None:
    # Mock BrokerService tokens retrieving
    with patch('app.routes.orders.BrokerService') as mock_broker_svc_class:
        mock_svc_instance = mock_broker_svc_class.return_value
        mock_svc_instance.get_decrypted_tokens = AsyncMock(return_value={"access_token": "token123"})
        
        # Setup mock client
        mock_client = AsyncMock()
        mock_client.connect.return_value = True
        
        # Setup rejected response
        class MockResponse:
            status: Any = type('obj', (object,), {'value': 'REJECTED'})
            message: str = "Insufficient margin"
            order_id: str = ""
        mock_client.place_order.return_value = MockResponse()
        
        mock_create_broker_client.return_value = mock_client
        
        # Action
        response = await async_client.post(
            "/api/v1/orders/place",
            json={
                "symbol": "TCS",
                "order_type": "MARKET",
                "side": "BUY",
                "quantity": 1,
                "broker_name": "angelone"
            }
        )
        
        assert response.status_code == 400
        assert "margin" in response.json()["detail"]
        
        mock_client.connect.assert_awaited()
        mock_client.place_order.assert_awaited()
        mock_client.disconnect.assert_awaited()
