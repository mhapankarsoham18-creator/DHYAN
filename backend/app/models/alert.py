from sqlalchemy import String, DateTime, ForeignKey, text, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
from datetime import datetime
from app.models.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    symbol: Mapped[str] = mapped_column(String, nullable=False, index=True)
    condition: Mapped[str] = mapped_column(String, nullable=False) # PRICE_ABOVE, PRICE_BELOW
    target_price: Mapped[float] = mapped_column(Float, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    
    user: Mapped["User"] = relationship("User", backref="alerts")
