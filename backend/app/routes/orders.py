"""Order placement route with concurrent-safe DB locking."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
import logging

from app.db.database import get_db
from app.models import User, Order
from app.services.auth_service import get_current_user
from app.services.broker import create_broker_client
from app.services.broker.interface import OrderRequest, OrderSide, OrderType, OrderStatus
from app.services.broker_service import BrokerService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])


class PlaceOrderRequest(BaseModel):
    symbol: str
    order_type: str  # MARKET, LIMIT
    side: str  # BUY, SELL
    quantity: int = Field(gt=0, le=10000, description="Order quantity must be between 1 and 10,000")
    price: Optional[float] = Field(default=None, gt=0, description="Price must be positive if provided")
    broker_name: str = "paper"  # Which broker to route to


@router.post("/place")
async def place_order(
    req: PlaceOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Place an order with concurrent-safe row-level locking."""
    # Row-level lock on the user to prevent race conditions
    await db.execute(
        text("SELECT 1 FROM users WHERE id = :uid FOR UPDATE"),
        {"uid": str(current_user.id)},
    )

    # Get broker client
    broker_client = None
    if req.broker_name != "paper":
        # Retrieve decrypted tokens from DB
        broker_svc = BrokerService(db)
        tokens = await broker_svc.get_decrypted_tokens(
            str(current_user.id), req.broker_name
        )
        if not tokens or not tokens.get("access_token"):
            raise HTTPException(
                status_code=503,
                detail=f"Broker '{req.broker_name}' not connected. Please authenticate first.",
            )
        broker_client = create_broker_client(
            req.broker_name,
            access_token=tokens["access_token"],
            refresh_token=tokens.get("refresh_token"),
        )
    else:
        broker_client = create_broker_client("paper")

    if broker_client is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported broker: {req.broker_name}",
        )

    # Connect to broker
    connected = await broker_client.connect()
    if not connected:
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to broker '{req.broker_name}'. "
                   "Check that API keys are configured in .env",
        )

    # Save order to database as PENDING
    db_order = Order(
        user_id=current_user.id,
        symbol=req.symbol,
        order_type=req.order_type,
        side=req.side,
        quantity=req.quantity,
        price=req.price or 0.0,
        status="PENDING",
    )
    db.add(db_order)
    await db.flush()  # Get the ID without committing

    # Build the broker order request
    try:
        order_side = OrderSide(req.side.upper())
        order_type = OrderType(req.order_type.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid side '{req.side}' or order_type '{req.order_type}'. "
                   "Use BUY/SELL and MARKET/LIMIT.",
        )

    broker_order = OrderRequest(
        symbol=req.symbol,
        side=order_side,
        order_type=order_type,
        quantity=req.quantity,
        price=req.price,
    )

    # Execute via broker
    try:
        response = await broker_client.place_order(broker_order)
    
        if response.status in (OrderStatus.EXECUTED, OrderStatus.PENDING):
            db_order.status = response.status.value
            db_order.broker_order_id = response.order_id
            if response.filled_price:
                db_order.price = response.filled_price
            await db.commit()
        else:
            db_order.status = "REJECTED"
            await db.commit()
            raise HTTPException(
                status_code=400,
                detail=response.message or "Order rejected by broker",
            )
    finally:
        # Disconnect
        await broker_client.disconnect()

    return {
        "status": "success",
        "order_id": str(db_order.id),
        "broker_order_id": response.order_id,
        "broker": req.broker_name,
        "message": response.message or "Order placed successfully",
    }
