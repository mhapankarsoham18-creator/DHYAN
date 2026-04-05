from sqlalchemy import Column, String, DateTime, text, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    razorpay_customer_id = Column(String, nullable=True, unique=True)
    razorpay_subscription_id = Column(String, nullable=True, unique=True)
    
    plan_id = Column(String, nullable=True) # e.g., 'plan_PXXX'
    status = Column(String, default="inactive") # active, inactive, past_due, canceled
    
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))

    # Relationship back to User
    user = relationship("User", back_populates="subscription")
