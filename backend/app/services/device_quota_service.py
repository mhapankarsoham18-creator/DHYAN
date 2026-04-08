from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.db.database import get_db
from app.models.device_quota import DeviceQuota

FREE_TIER_MONTHLY_LIMIT = 10

def extract_device_fingerprint(request: Request) -> Optional[str]:
    """Extracts the secure hardware footprint from the request header."""
    return request.headers.get("X-Device-Fingerprint")

async def verify_device_quota(
    request: Request,
    db: AsyncSession = Depends(get_db)
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
    current_month = datetime.utcnow().strftime("%Y-%m")
    
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

    # Increment usage inside the actual route or here?
    # Doing it here consumes a token merely by hitting the endpoint.
    quota_record.free_trades_used += 1
    await db.commit()
    
    return True
