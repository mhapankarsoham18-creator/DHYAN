"""Order routing service — async, no mocks."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.order import Order
import logging

logger = logging.getLogger(__name__)


class OrderRoutingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_order(self, order_id: str) -> Order | None:
        """Retrieve an order by ID."""
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        return result.scalars().first()

    async def update_order_status(
        self, order_id: str, status: str, broker_order_id: str | None = None
    ) -> Order | None:
        """Update order status from broker callback or polling."""
        order = await self.get_order(order_id)
        if not order:
            return None

        order.status = status
        if broker_order_id:
            order.broker_order_id = broker_order_id

        await self.db.commit()
        logger.info("Order %s status updated to %s", order_id, status)
        return order

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order."""
        order = await self.get_order(order_id)
        if not order or order.status != "PENDING":
            return False

        order.status = "CANCELLED"
        await self.db.commit()
        logger.info("Order %s cancelled", order_id)
        return True

    async def get_user_orders(self, user_id: str, limit: int = 50) -> list[Order]:
        """Get recent orders for a user."""
        result = await self.db.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
