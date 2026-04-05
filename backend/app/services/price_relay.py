"""WebSocket price relay — live market data streaming.

Connects to real broker WebSocket feeds during market hours.
No mock/simulated price generation.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Set, Optional, Any
import asyncio
import json
import logging
from datetime import datetime, time as dt_time
import pytz

from app.services.broker.interface import BrokerInterface

logger = logging.getLogger(__name__)

IST = pytz.timezone("Asia/Kolkata")
MARKET_OPEN = dt_time(9, 15)
MARKET_CLOSE = dt_time(15, 30)


def is_market_hours() -> bool:
    """Check if current time is within NSE trading hours (IST)."""
    now = datetime.now(IST).time()
    return MARKET_OPEN <= now <= MARKET_CLOSE


class PriceRelay:
    """Manages WebSocket connections and broadcasts real-time prices."""

    def __init__(self) -> None:
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._broker_feed_task: Optional[asyncio.Task[Any]] = None

    async def connect(self, websocket: WebSocket, symbols: List[str]) -> None:
        await websocket.accept()
        for symbol in symbols:
            if symbol not in self.active_connections:
                self.active_connections[symbol] = set()
            self.active_connections[symbol].add(websocket)
        logger.info("WebSocket connected for symbols: %s", symbols)

    def disconnect(self, websocket: WebSocket) -> None:
        for symbol in list(self.active_connections.keys()):
            self.active_connections[symbol].discard(websocket)
            if not self.active_connections[symbol]:
                del self.active_connections[symbol]
        logger.info("WebSocket disconnected")

    async def broadcast_price(self, symbol: str, price: float) -> None:
        """Broadcast a price update to all subscribers of a symbol."""
        if symbol not in self.active_connections:
            return

        message = json.dumps({"symbol": symbol, "price": price, "timestamp": datetime.now(IST).isoformat()})
        dead_connections: List[WebSocket] = []

        for connection in self.active_connections[symbol]:
            try:
                await connection.send_text(message)
            except Exception:
                dead_connections.append(connection)

        # Clean up dead connections
        for dead in dead_connections:
            self.disconnect(dead)

    async def start_broker_feed(
        self, broker_client: BrokerInterface, symbols: List[str]
    ) -> None:
        """Connect to real broker WebSocket feed and relay prices.

        This polls the broker's quote API at a configurable interval.
        For brokers with native WebSocket support, this can be overridden
        with a streaming implementation.
        """
        backoff = 1
        max_backoff = 60

        while True:
            if not is_market_hours():
                logger.info("Outside market hours. Waiting...")
                await asyncio.sleep(60)
                continue

            if not self.active_connections:
                await asyncio.sleep(5)
                continue

            try:
                connected = await broker_client.connect()
                if not connected:
                    logger.warning(
                        "Broker feed connection failed. Retrying in %ds...", backoff
                    )
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, max_backoff)
                    continue

                backoff = 1  # Reset on success

                # Poll quotes for subscribed symbols
                subscribed_symbols = list(self.active_connections.keys())
                for symbol in subscribed_symbols:
                    try:
                        quote = await broker_client.get_quote(symbol)
                        if quote.last_price > 0:
                            await self.broadcast_price(symbol, quote.last_price)
                    except Exception as e:
                        logger.error("Error fetching quote for %s: %s", symbol, e)

                await asyncio.sleep(1)  # 1-second polling interval

            except Exception as e:
                logger.error("Broker feed error: %s. Reconnecting in %ds...", e, backoff)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, max_backoff)


price_relay = PriceRelay()

router = APIRouter()


@router.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """WebSocket endpoint for receiving live price updates.

    Client sends a JSON message with symbols to subscribe:
    {"action": "subscribe", "symbols": ["RELIANCE", "INFY"]}
    """
    await websocket.accept()
    symbols: List[str] = []

    try:
        # Wait for initial subscription message
        data = await websocket.receive_text()
        msg = json.loads(data)
        symbols = msg.get("symbols", [])

        if not symbols:
            await websocket.send_text(
                json.dumps({"error": "No symbols provided. Send: {\"symbols\": [\"RELIANCE\"]}"})
            )
            await websocket.close()
            return

        # Register subscriptions
        for symbol in symbols:
            if symbol not in price_relay.active_connections:
                price_relay.active_connections[symbol] = set()
            price_relay.active_connections[symbol].add(websocket)

        logger.info("WS subscribed to: %s", symbols)

        if not is_market_hours():
            await websocket.send_text(
                json.dumps({
                    "info": "Market is closed. Prices will stream during market hours (9:15 AM - 3:30 PM IST)."
                })
            )

        # Keep connection alive
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        price_relay.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error: %s", e)
        price_relay.disconnect(websocket)
