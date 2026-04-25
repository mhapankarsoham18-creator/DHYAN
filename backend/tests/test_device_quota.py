# pyright: reportMissingImports=false, reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import Request, HTTPException
from app.services.device_quota_service import verify_device_quota

pytestmark = pytest.mark.asyncio

@patch("app.core.redis.upstash_redis")
async def test_verify_device_quota_under_limit(mock_redis: AsyncMock) -> None:
    request = MagicMock(spec=Request)
    request.headers = {"X-Device-Fingerprint": "device_123"}
    
    mock_redis.incr.return_value = 5 # 5th use
    
    mock_db = AsyncMock()
    
    # Should not raise exception
    _ = await verify_device_quota(request=request, db=mock_db)
    
    # Redis incr should be called
    mock_redis.incr.assert_called_once()
    mock_redis.expire.assert_not_called()

@patch("app.core.redis.upstash_redis")
async def test_verify_device_quota_first_use(mock_redis: AsyncMock) -> None:
    request = MagicMock(spec=Request)
    request.headers = {"X-Device-Fingerprint": "device_abc"}
    
    mock_redis.incr.return_value = 1 # 1st use
    
    mock_db = AsyncMock()
    
    _ = await verify_device_quota(request, mock_db)
    
    mock_redis.expire.assert_called_once()

@patch("app.core.redis.upstash_redis")
async def test_verify_device_quota_over_limit(mock_redis: AsyncMock) -> None:
    request = MagicMock(spec=Request)
    request.headers = {"X-Device-Fingerprint": "device_spam"}
    
    mock_redis.incr.return_value = 11 # 11th use, over limit (10)
    
    mock_db = AsyncMock()
    
    with pytest.raises(HTTPException) as exc:
        _ = await verify_device_quota(request=request, db=mock_db)
    
    assert exc.value.status_code == 429
    assert "Free tier limit" in exc.value.detail

@patch("app.core.redis.upstash_redis", None)
async def test_verify_device_quota_redis_fallback() -> None:
    request = MagicMock(spec=Request)
    request.headers = {"X-Device-Fingerprint": "device_postgres"}
    
    mock_db = AsyncMock()
    mock_db_result = MagicMock()
    mock_db_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_db_result
    
    _ = await verify_device_quota(request, mock_db)
    
    assert mock_db.add.called
    assert mock_db.commit.called
