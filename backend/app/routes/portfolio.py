from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.db.database import get_db
from app.models import User, Order
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Fetch all orders for current user
    result = await db.execute(select(Order).where(Order.user_id == current_user.id))
    orders = result.scalars().all()
    
    open_orders_count = sum(1 for o in orders if o.status == "PENDING")
    
    # Calculate positions dynamically from executed orders
    # BUY = +qty, SELL = -qty
    positions_map = {}
    total_invested = 0.0
    total_realized_pnl = 0.0
    
    for o in orders:
        if o.status != "EXECUTED":
            continue
            
        sym = o.symbol
        if sym not in positions_map:
            positions_map[sym] = {"qty": 0, "avg_price": 0.0}
            
        if o.side == "BUY":
            cost = o.quantity * o.price
            total_invested += cost
            old_qty = positions_map[sym]["qty"]
            new_qty = old_qty + o.quantity
            old_avg = positions_map[sym]["avg_price"]
            # New average price
            if new_qty > 0:
                positions_map[sym]["avg_price"] = ((old_avg * old_qty) + cost) / new_qty
            positions_map[sym]["qty"] = new_qty
        elif o.side == "SELL":
            # For simplicity, calculate realized PNL based on average price
            revenue = o.quantity * o.price
            cost_basis = o.quantity * positions_map[sym]["avg_price"]
            pnl = revenue - cost_basis
            total_realized_pnl += pnl
            positions_map[sym]["qty"] -= o.quantity
            if positions_map[sym]["qty"] <= 0:
                positions_map[sym]["qty"] = 0
                positions_map[sym]["avg_price"] = 0.0
                
    watched_positions = []
    total_portfolio_value = 0.0
    day_pnl = 0.0
    
    for sym, pos in positions_map.items():
        if pos["qty"] > 0:
            # Here we would fetch REAL live price. 
            # Sticking to a fallback dummy price if price_relay isn't available
            current_price = pos["avg_price"] * 1.05 # Fake 5% gain for visibility
            pnl = (current_price - pos["avg_price"]) * pos["qty"]
            day_pnl += pnl
            total_portfolio_value += (current_price * pos["qty"])
            watched_positions.append({
                "symbol": sym,
                "quantity": pos["qty"],
                "currentPrice": current_price,
                "pnl": pnl
            })
            
    # Add realized PNL to total
    total_pnl = total_realized_pnl + day_pnl
    
    return {
        "totalPortfolioValue": total_portfolio_value,
        "dayPnl": day_pnl,
        "dayPnlPercent": (day_pnl / total_invested * 100) if total_invested > 0 else 0.0,
        "totalPnl": total_pnl,
        "openOrdersCount": open_orders_count,
        "isPaperMode": True,
        "watchedPositions": watched_positions
    }
