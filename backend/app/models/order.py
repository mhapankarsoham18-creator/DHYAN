from sqlalchemy import String, DateTime, ForeignKey, text, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
from datetime import datetime
from app.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.broker_connection import BrokerConnection

class Order(Base):
    __tablename__: str = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    broker_connection_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("broker_connections.id", ondelete="SET NULL"), nullable=True)
    
    symbol: Mapped[str] = mapped_column(String, nullable=False, index=True)
    order_type: Mapped[str] = mapped_column(String, nullable=False) # MARKET, LIMIT
    side: Mapped[str] = mapped_column(String, nullable=False) # BUY, SELL
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float | None] = mapped_column(Float, nullable=True) # None for MARKET orders
    fees: Mapped[float | None] = mapped_column(Float, nullable=True) # Statutory + platform fees
    broker_order_id: Mapped[str | None] = mapped_column(String, nullable=True) # Real broker's order reference
    
    status: Mapped[str] = mapped_column(String, nullable=False, default="PENDING") # PENDING, EXECUTED, REJECTED, CANCELLED
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))

    user: Mapped["User"] = relationship("User", backref="orders")
    broker_connection: Mapped["BrokerConnection"] = relationship("BrokerConnection", backref="orders")
