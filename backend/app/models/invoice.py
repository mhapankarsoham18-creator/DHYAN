from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
import uuid
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base

class Invoice(Base):
    __tablename__: str = "invoices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Financials (in paise or cents to avoid float issues, but storing float as per Razorpay standard response if preferred. Let's use Float for simplicity but recommend Integer for Prod)
    amount_base: Mapped[float] = mapped_column(Float, nullable=False)  # Base amount before tax
    cgst: Mapped[float] = mapped_column(Float, nullable=False)         # 9%
    sgst: Mapped[float] = mapped_column(Float, nullable=False)         # 9%
    total_amount: Mapped[float] = mapped_column(Float, nullable=False) # Base + CGST + SGST
    
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    receipt_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<Invoice(id={self.id}, user_id={self.user_id}, total={self.total_amount})>"
