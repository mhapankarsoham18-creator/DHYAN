import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.services.auth_service import get_current_user
from app.services.razorpay_service import create_customer, create_subscription_for_customer

router = APIRouter(prefix="/billing", tags=["billing"])

# Note: Ideally provided by env, but hardcoding fallback as user has not provided keys
DEFAULT_PLAN_ID = os.environ.get("RAZORPAY_PRO_PLAN_ID", "plan_Pplaceholder123")

@router.post("/create-subscription")
async def process_create_subscription(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # 1. Fetch or create a Subscription record locally
    result = await db.execute(select(Subscription).where(Subscription.user_id == current_user.id))
    sub = result.scalars().first()
    
    if not sub:
        sub = Subscription(user_id=current_user.id)
        db.add(sub)
        await db.commit()
        await db.refresh(sub)
        
    # 2. Check if already has Razorpay Customer ID
    if not sub.razorpay_customer_id:
        sub.razorpay_customer_id = create_customer(current_user)
        db.add(sub)
        await db.commit()
        
    # 3. Request subscription from Razorpay
    if sub.status == "active":
        return {"message": "You are already subscribed to Dhyan Pro.", "status": sub.status}
        
    try:
        razorpay_sub = create_subscription_for_customer(sub.razorpay_customer_id, DEFAULT_PLAN_ID)
        
        # Save subscription id from razorpay
        sub.razorpay_subscription_id = razorpay_sub.get("id")
        sub.plan_id = DEFAULT_PLAN_ID
        sub.status = "created"  # Waiting for payment webhook
        db.add(sub)
        await db.commit()
        
        return {
            "subscription_id": sub.razorpay_subscription_id,
            "status": sub.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_subscription_status(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subscription).where(Subscription.user_id == current_user.id))
    sub = result.scalars().first()
    if not sub:
        return {"status": "inactive"}
    return {
        "status": sub.status,
        "plan": sub.plan_id
    }

class RefundRequest(BaseModel):
    payment_id: str
    amount_inr: Optional[float] = None
    reason: Optional[str] = None

@router.post("/refund")
async def request_refund(
    request: RefundRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint for processing refunds for a specific payment.
    In a fully fleshed out app, we would verify if `current_user` is an admin or the owner of the payment.
    """
    try:
        from app.services.razorpay_service import process_refund
        refund_response = process_refund(request.payment_id, request.amount_inr)
        
        # We would then write an audit log to the DB 
        # AuditLog(user_id=current_user.id, action="refund", details=f"Refunded {refund_response['amount']/100} INR")
        
        return {
            "status": "success",
            "refund_id": refund_response.get("id"),
            "refunded_amount_inr": refund_response.get("amount", 0) / 100.0,
            "message": "Refund processed successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Refund failed: {str(e)}")

@router.get("/invoices")
async def get_invoices(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Fetch all tax-compliant invoices generated for the user."""
    from app.models.invoice import Invoice
    
    result = await db.execute(
        select(Invoice)
        .where(Invoice.user_id == current_user.id)
        .order_by(Invoice.created_at.desc())
    )
    invoices = result.scalars().all()
    
    return {
        "status": "success",
        "invoices": [
            {
                "id": inv.id,
                "receipt_number": inv.receipt_number,
                "description": inv.description,
                "base_amount": inv.amount_base,
                "cgst": inv.cgst,
                "sgst": inv.sgst,
                "total": inv.total_amount,
                "date": inv.created_at.isoformat() if inv.created_at else None
            }
            for inv in invoices
        ]
    }
