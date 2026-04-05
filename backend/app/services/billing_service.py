import logging
import uuid
from datetime import datetime, timezone


logger = logging.getLogger(__name__)

class BillingService:
    COMPANY_NAME: str = "Dhyan Analytics"
    GSTIN: str = "dhyan"
    GST_RATE: float = 0.18  # 18% GST (9% CGST + 9% SGST/IGST typically, simplified here)

    @staticmethod
    def generate_invoice(user_id: str, payment_id: str, amount_inr: float) -> dict[str, str | float]:
        """Generate a mock PDF invoice record with GST breakdown."""
        gst_amount = amount_inr * BillingService.GST_RATE
        base_amount = amount_inr - gst_amount

        invoice_record = {
            "invoice_id": f"INV-{uuid.uuid4().hex[:8].upper()}",
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
        # In a real system, you would generate a PDF via ReportLab here and upload to S3/Supabase Storage
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
