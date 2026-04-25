from typing import Annotated
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.db.database import get_db
from app.models.device_quota import DeviceQuota

FREE_TIER_MONTHLY_LIMIT = 10

def extract_device_fingerprint(request: Request) -> str | None:
    """Extracts the secure hardware footprint from the request header."""
    return request.headers.get("X-Device-Fingerprint")

async def verify_device_quota(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Dependency that enforces free tier trades by validating
    the unique hardware fingerprint.
    
    In a real app, you would check if the user is a Premium subscriber.
    If premium, bypass the quota check.
    For now, we just enforce the hardware limit.
    """
    fingerprint = extract_device_fingerprint(request)
    
    if not fingerprint:
        # If no fingerprint is provided, block the request if it's required,
        # but for progressive enhancement, we'll allow it or apply a strict IP limit.
        return True

    # Current YYYY-MM
    current_month = datetime.now(timezone.utc).strftime("%Y-%m")
    
    # 1. Try Upstash Redis first for blazing fast rate limiting
    from app.core.redis import upstash_redis
    
    if upstash_redis:
        redis_key = f"quota:device:{fingerprint}:{current_month}"
        
        # Atomically increment and get the current usage
        current_usage = await upstash_redis.incr(redis_key)
        
        # If this is the first time (usage == 1), set an expiry of 31 days
        if current_usage == 1:
            _ = await upstash_redis.expire(redis_key, 31 * 24 * 60 * 60)
            
        if current_usage > FREE_TIER_MONTHLY_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Free tier limit reached ({FREE_TIER_MONTHLY_LIMIT} requests/month). Please upgrade to Pro."
            )
        return True

    # 2. Fallback to PostgreSQL if Redis is not configured
    query = select(DeviceQuota).where(
        DeviceQuota.device_id == fingerprint,
        DeviceQuota.month_period == current_month
    )
    result = await db.execute(query)
    quota_record = result.scalar_one_or_none()

    if not quota_record:
        # Create a new quota entry for this month
        quota_record = DeviceQuota(
            device_id=fingerprint,
            month_period=current_month,
            free_trades_used=0
        )
        db.add(quota_record)
        await db.commit()
    
    if quota_record.free_trades_used >= FREE_TIER_MONTHLY_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Free tier limit reached ({FREE_TIER_MONTHLY_LIMIT} requests/month). Please upgrade to Pro."
        )

    # Increment usage
    quota_record.free_trades_used += 1
    await db.commit()
    
    return True
