from sqlalchemy import String, Integer, DateTime, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class DeviceQuota(Base):
    __tablename__ = "device_quotas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    device_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    month_period: Mapped[str] = mapped_column(String, nullable=False, index=True) # e.g., "2023-10"
    free_trades_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))

    __table_args__ = (
        UniqueConstraint('device_id', 'month_period', name='uq_device_month'),
    )
