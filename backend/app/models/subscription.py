from sqlalchemy import String, DateTime, text, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.models.base import Base

class Subscription(Base):
    __tablename__: str = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    razorpay_customer_id: Mapped[str | None] = mapped_column(String, nullable=True, unique=True)
    razorpay_subscription_id: Mapped[str | None] = mapped_column(String, nullable=True, unique=True)
    
    plan_id: Mapped[str | None] = mapped_column(String, nullable=True) # e.g., 'plan_PXXX'
    status: Mapped[str] = mapped_column(String, default="inactive") # active, inactive, past_due, canceled
    
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))

    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="subscription")
