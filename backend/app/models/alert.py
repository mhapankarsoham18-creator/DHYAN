from sqlalchemy import Column, String, DateTime, ForeignKey, text, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    symbol = Column(String, nullable=False, index=True)
    condition = Column(String, nullable=False) # PRICE_ABOVE, PRICE_BELOW
    target_price = Column(Float, nullable=False)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    
    user = relationship("User", backref="alerts")
