from sqlalchemy import String, DateTime, Boolean, text, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.subscription import Subscription

class User(Base):
    __tablename__: str = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    phone_number: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    
    # Paper Trading / Simulation Mode
    simulation_active: Mapped[bool] = mapped_column(Boolean, default=False)
    simulation_start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    virtual_balance: Mapped[float] = mapped_column(Float, default=0.0)

    # Subscriptions
    subscription: Mapped["Subscription | None"] = relationship("Subscription", back_populates="user", uselist=False)
