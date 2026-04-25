import logging
import uuid
from datetime import datetime, timezone


logger = logging.getLogger(__name__)

class BillingService:
    COMPANY_NAME: str = "Dhyan Analytics"
    GSTIN: str = "dhyan"
    GST_RATE: float = 0.18  # 18% GST (9% CGST + 9% SGST/IGST typically, simplified here)

    @staticmethod
    async def generate_invoice(db, user_id: str, payment_id: str, amount_inr: float) -> dict[str, str | float]:
        """Generate a mock PDF invoice record with GST breakdown and persist it to DB."""
        from app.models.invoice import Invoice
        
        gst_amount = amount_inr * BillingService.GST_RATE
        cgst_amount = gst_amount / 2
        sgst_amount = gst_amount / 2
        base_amount = amount_inr - gst_amount

        invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"

        db_invoice = Invoice(
            user_id=user_id,
            amount_base=round(base_amount, 2),
            cgst=round(cgst_amount, 2),
            sgst=round(sgst_amount, 2),
            total_amount=round(amount_inr, 2),
            description=f"Subscription Payment: {payment_id}",
            receipt_number=invoice_id
        )
        db.add(db_invoice)
        # We don't commit here, we let the caller (webhook) commit the entire transaction
        
        invoice_record = {
            "invoice_id": invoice_id,
            "date": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "payment_id": payment_id,
            "company": BillingService.COMPANY_NAME,
            "gstin": BillingService.GSTIN,
            "base_amount": round(base_amount, 2),
            "gst_amount": round(gst_amount, 2),
            "total_amount": round(amount_inr, 2),
            "currency": "INR",
        }
        
        logger.info(f"Generated Invoice {invoice_record['invoice_id']} for User {user_id}")
        return invoice_record

    @staticmethod
    def send_receipt_email(user_email: str, invoice: dict[str, str | float]) -> bool:
        """Mock dispatcher for receipt emails."""
        logger.info(
            f"Sending Receipt to {user_email}: " +
            f"Billed ₹{invoice['total_amount']} " +
            f"(includes ₹{invoice['gst_amount']} GST)"
        )
        # Placeholder for SendGrid / AWS SES logic
        return True
