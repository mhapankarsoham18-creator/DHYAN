from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.models import User, Alert
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])

class CreateAlertRequest(BaseModel):
    symbol: str
    target_price: float
    condition: str
    
@router.get("")
async def get_alerts(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Alert).where(Alert.user_id == current_user.id))
    alerts = result.scalars().all()
    
    return [
        {
            "id": str(a.id) if hasattr(a, 'id') else "",
            "symbol": str(getattr(a, 'symbol', "")),
            "condition": str(getattr(a, 'condition', "")),
            "targetPrice": float(getattr(a, 'target_price', 0.0)),
            "isTriggered": bool(getattr(a, 'is_triggered', False)),
            "createdAt": getattr(a, 'created_at', None)
        } for a in alerts
    ]

@router.post("")
async def create_alert(
    req: CreateAlertRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    new_alert = Alert(
        user_id=current_user.id,
        symbol=req.symbol,
        target_price=req.target_price,
        condition=req.condition,
        is_triggered=False
    )
    db.add(new_alert)
    await db.commit()
    await db.refresh(new_alert)
    return {"status": "success", "id": str(new_alert.id)}

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id, Alert.user_id == current_user.id))
    alert = result.scalars().first()
    if alert:
        await db.delete(alert)
        await db.commit()
    return {"status": "success"}
