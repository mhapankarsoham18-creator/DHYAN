# pyright: reportMissingImports=false, reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.token_refresh_service import TokenRefreshService
from app.models.broker_connection import BrokerConnection

pytestmark = pytest.mark.asyncio

@patch("app.services.token_refresh_service.SessionLocal")
@patch("app.services.token_refresh_service.create_broker_client")
async def test_refresh_all_active_tokens(mock_create_broker_client: MagicMock, mock_session_local: MagicMock) -> None:
    # Setup mock DB and async context manager
    mock_db = AsyncMock()
    mock_session_local.return_value.__aenter__.return_value = mock_db
    
    # Setup mock connection
    mock_conn = BrokerConnection(
        id="123",
        user_id="user456",
        broker_name="shoonya",
        is_active=True,
    )
    
    # Mocking db.execute(stmt).scalars().all() -> [mock_conn]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_conn]
    mock_db.execute.return_value = mock_result
    
    # Setup mock broker client
    mock_broker = AsyncMock()
    mock_broker.refresh_session.return_value = {
        "access_token": "new.access.token",
        "refresh_token": "new.refresh.token"
    }
    mock_create_broker_client.return_value = mock_broker
    
    # Run service
    service = TokenRefreshService()
    await service.refresh_all_active_tokens()
    
    # Verify broker was called
    mock_create_broker_client.assert_called_once()
    mock_broker.refresh_session.assert_awaited_once()
    
    # Verify DB save
    assert mock_conn.access_token is not None  # It was encrypted
    assert mock_conn.refresh_token is not None
    mock_db.commit.assert_awaited_once()

@patch("app.services.token_refresh_service.SessionLocal")
@patch("app.services.token_refresh_service.create_broker_client")
async def test_refresh_skips_when_no_active_tokens(mock_create_broker_client: MagicMock, mock_session_local: MagicMock) -> None:
    mock_db = AsyncMock()
    mock_session_local.return_value.__aenter__.return_value = mock_db
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    
    service = TokenRefreshService()
    await service.refresh_all_active_tokens()
    
    mock_create_broker_client.assert_not_called()
    mock_db.commit.assert_not_called()
