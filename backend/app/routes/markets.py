"""Markets route — no mock/hardcoded data.

Returns simulation data for users in simulation mode.
Returns 'unavailable' message when no broker is connected.
Once broker keys are configured and user connects a broker,
returns real market data from the broker's quote API.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.models import User
from app.models.broker_connection import BrokerConnection
from app.services.auth_service import get_current_user
from app.services.broker import create_broker_client
from app.services.broker_service import BrokerService
from app.services.simulation_service import (
    get_simulated_market_overview,
    is_simulation_expired,
)

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("/overview")
async def get_markets_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check if user is in active simulation mode
    if current_user.simulation_active and current_user.simulation_start_date:
        if is_simulation_expired(current_user.simulation_start_date):
            # Auto-deactivate expired simulation
            current_user.simulation_active = False
            db.add(current_user)
            await db.commit()
        else:
            return get_simulated_market_overview(
                str(current_user.id),
                current_user.simulation_start_date,
            )

    # Check if user has an active broker connection
    result = await db.execute(
        select(BrokerConnection).where(
            BrokerConnection.user_id == current_user.id,
            BrokerConnection.is_active == True,  # noqa: E712
        )
    )
    active_broker = result.scalars().first()

    if not active_broker:
        return {
            "market_data_available": False,
            "is_simulation": False,
            "message": "Connect a broker to see live market data, or start a simulation to practice.",
            "indices": [],
            "topGainers": [],
            "topLosers": [],
            "activeSectors": [],
        }

    # Try to fetch real market data from connected broker
    broker_svc = BrokerService(db)
    tokens = await broker_svc.get_decrypted_tokens(
        str(current_user.id), active_broker.broker_name
    )

    if not tokens or not tokens.get("access_token"):
        return {
            "market_data_available": False,
            "is_simulation": False,
            "message": f"Broker '{active_broker.broker_name}' session expired. Please re-authenticate.",
            "indices": [],
            "topGainers": [],
            "topLosers": [],
            "activeSectors": [],
        }

    client = create_broker_client(
        active_broker.broker_name,
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),
    )

    if not client:
        return {
            "market_data_available": False,
            "is_simulation": False,
            "message": f"Broker '{active_broker.broker_name}' is not supported.",
            "indices": [],
            "topGainers": [],
            "topLosers": [],
            "activeSectors": [],
        }

    connected = await client.connect()
    if not connected:
        return {
            "market_data_available": False,
            "is_simulation": False,
            "message": f"Could not connect to '{active_broker.broker_name}'. Check API keys.",
            "indices": [],
            "topGainers": [],
            "topLosers": [],
            "activeSectors": [],
        }

    # Fetch quotes for key indices/symbols
    index_symbols = ["NIFTY 50", "NIFTY BANK"]
    indices = []
    for sym in index_symbols:
        quote = await client.get_quote(sym)
        if quote.last_price > 0:
            indices.append({
                "symbol": sym,
                "value": quote.last_price,
                "change": 0,  # Delta requires historical comparison
                "changePercent": 0,
            })

    await client.disconnect()

    return {
        "market_data_available": True,
        "is_simulation": False,
        "broker": active_broker.broker_name,
        "indices": indices,
        "topGainers": [],  # Requires full market scan — future enhancement
        "topLosers": [],
        "activeSectors": [],
    }
