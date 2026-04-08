# pyright: reportMissingImports=false, reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import pytest
from fastapi import Request, HTTPException
from unittest.mock import MagicMock, AsyncMock

from app.services.device_quota_service import verify_device_quota, FREE_TIER_MONTHLY_LIMIT
from app.models.device_quota import DeviceQuota

pytestmark = pytest.mark.asyncio

async def test_verify_device_quota_no_fingerprint(mock_db_session: AsyncMock) -> None:
    request = MagicMock(spec=Request)
    request.headers = {}
    
    result = await verify_device_quota(request, mock_db_session)
    assert result is True

async def test_verify_device_quota_first_time(mock_db_session: AsyncMock) -> None:
    request = MagicMock(spec=Request)
    request.headers = {"X-Device-Fingerprint": "mock_fp_123"}
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    
    result = await verify_device_quota(request, mock_db_session)
    assert result is True
    assert mock_db_session.add.called
    assert mock_db_session.commit.call_count >= 1

async def test_verify_device_quota_within_limit(mock_db_session: AsyncMock) -> None:
    request = MagicMock(spec=Request)
    request.headers = {"X-Device-Fingerprint": "mock_fp_123"}
    
    quota = DeviceQuota(device_id="mock_fp_123", month_period="2026-04", free_trades_used=5) # type: ignore
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = quota
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    
    result = await verify_device_quota(request, mock_db_session)
    assert result is True
    assert quota.free_trades_used == 6
    assert mock_db_session.commit.call_count == 1

async def test_verify_device_quota_exceeds_limit(mock_db_session: AsyncMock) -> None:
    request = MagicMock(spec=Request)
    request.headers = {"X-Device-Fingerprint": "mock_fp_123"}
    
    quota = DeviceQuota(device_id="mock_fp_123", month_period="2026-04", free_trades_used=FREE_TIER_MONTHLY_LIMIT) # type: ignore
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = quota
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    
    with pytest.raises(HTTPException) as exc_info:
        _ = await verify_device_quota(request, mock_db_session)
    
    assert exc_info.value.status_code == 429
