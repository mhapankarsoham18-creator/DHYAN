# pyright: reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Any, cast, Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json
import logging

from app.db.database import get_db
from app.models.subscription import Subscription
from app.services.razorpay_service import verify_webhook_signature
from app.services.billing_service import BillingService
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/razorpay")
async def razorpay_webhook(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    """Handles asynchronous webhook callbacks from Razorpay."""
    payload_body = await request.body()
    signature = request.headers.get("x-razorpay-signature")

    if not signature:
        logger.warning("Razorpay Webhook rejected: No Signature Header")
        raise HTTPException(status_code=400, detail="Missing signature")

    # Cryptographically verify the payload
    is_valid = verify_webhook_signature(payload_body.decode('utf-8'), signature)
    
    if not is_valid:
        logger.error("Razorpay Webhook rejected: Invalid Signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # If valid, parse the event
    try:
        event = cast(dict[str, Any], json.loads(payload_body))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event_type = event.get("event")
    payload = event.get("payload", {})
    
    if isinstance(payload, dict) and "subscription" in payload:
        subscription_obj = cast(dict[str, Any], payload.get("subscription", {}))
        sub_data = cast(dict[str, Any], subscription_obj.get("entity", {}))
        razorpay_sub_id = cast(str, sub_data.get("id"))
        
        # Locate local subscription by razorpay id
        result = await db.execute(select(Subscription).where(Subscription.razorpay_subscription_id == razorpay_sub_id)) # type: ignore
        local_sub = result.scalars().first()
        
        if local_sub:
            if event_type == "subscription.charged":
                setattr(local_sub, "status", "active")
                
                # Fetch user to generate invoice + send email
                user_result = await db.execute(select(User).where(User.id == local_sub.user_id))
                sub_user = user_result.scalars().first()
                if sub_user:
                    # In a real payload, payment_id and amount come from the payload.
                    # We use mocks safely here if keys are missing.
                    payment_id_payload = cast(dict[str, Any], payload.get("payment", {})).get("entity", {}).get("id", "pay_mock_123")
                    payment_amount = cast(dict[str, Any], payload.get("payment", {})).get("entity", {}).get("amount", 99900)
                    amount_inr = payment_amount / 100.0  # Convert paise to INR
                    
                    invoice = await BillingService.generate_invoice(db, str(sub_user.id), payment_id_payload, amount_inr)
                    BillingService.send_receipt_email(sub_user.phone_number or "user@example.com", invoice)
                
            elif event_type in ["subscription.cancelled", "subscription.halted"]:
                setattr(local_sub, "status", "inactive")
                
            db.add(local_sub)
            await db.commit()
            logger.info(f"Subscription {razorpay_sub_id} updated to {getattr(local_sub, 'status')} via webhook.")
            
    return {"status": "ok"}
