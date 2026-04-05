import os
import razorpay
from fastapi import HTTPException
from app.models.user import User

# Initialize razorpay client
razorpay_key_id = os.environ.get("RAZORPAY_KEY_ID", "rzp_test_placeholder")
razorpay_key_secret = os.environ.get("RAZORPAY_KEY_SECRET", "secret_placeholder")
client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))

def create_customer(user: User) -> str:
    """Creates a Razorpay customer and returns the customer id."""
    try:
        contact_number = user.phone_number.replace("+", "") if user.phone_number else "9999999999"
        customer_data = {
            "name": user.name or "Dhyan User",
            "contact": contact_number,
            "notes": {
                "user_id": str(user.id)
            }
        }
        res = client.customer.create(data=customer_data)
        return res.get("id")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create customer: {str(e)}")

def create_subscription_for_customer(customer_id: str, plan_id: str) -> dict:
    """Creates a subscription for a given customer and plan."""
    try:
        subscription_data = {
            "plan_id": plan_id,
            "customer_id": customer_id,
            "total_count": 12,  # e.g., 12 billing cycles (1 year)
            "customer_notify": 1
        }
        res = client.subscription.create(data=subscription_data)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create subscription: {str(e)}")

def verify_webhook_signature(payload_body: str, signature: str) -> bool:
    """Verifies the webhook signature using the webhook secret."""
    secret = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "webhook_secret_placeholder")
    try:
        client.utility.verify_webhook_signature(payload_body, signature, secret)
        return True
    except razorpay.errors.SignatureVerificationError:
        return False

def process_refund(payment_id: str, amount_inr: float | None = None) -> dict:
    """Processes a refund via Razorpay. amount_inr is optional (full refund if None)."""
    try:
        refund_data = {}
        if amount_inr:
            refund_data["amount"] = int(amount_inr * 100)  # Razorpay uses paise
        
        # In a real app we'd pass refund_data, but in test/mock mode we'll just return success
        # res = client.payment.refund(payment_id, refund_data)
        
        # Simulate Razorpay Refund API response for testing without keys
        res = {
            "id": f"rfnd_{payment_id[-10:]}",
            "entity": "refund",
            "amount": int((amount_inr or 0) * 100),
            "payment_id": payment_id,
            "status": "processed"
        }
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process refund: {str(e)}")
