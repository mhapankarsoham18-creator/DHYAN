"""Upstox broker client.

Implements BrokerInterface using the upstox-python-sdk.
Requires env vars: UPSTOX_CLIENT_ID, UPSTOX_CLIENT_SECRET
"""
import os
import logging
from typing import Optional, Any

from app.services.broker.interface import (
    BrokerInterface,
    OrderRequest,
    OrderResponse,
    OrderSide,
    OrderStatus,
    OrderType,
    Position,
    Quote,
)

logger = logging.getLogger(__name__)

CLIENT_ID = os.getenv("UPSTOX_CLIENT_ID")
CLIENT_SECRET = os.getenv("UPSTOX_CLIENT_SECRET")


class UpstoxClient(BrokerInterface):
    """Upstox broker integration via REST API."""

    def __init__(
        self,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ):
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._connected = False
        self._headers: dict[str, str] = {}

    async def connect(self) -> bool:
        if not CLIENT_ID or not CLIENT_SECRET:
            logger.error(
                "Upstox API keys not configured. "
                "Set UPSTOX_CLIENT_ID and UPSTOX_CLIENT_SECRET in .env"
            )
            return False

        if not self._access_token:
            logger.error("Upstox access token not provided")
            return False

        self._headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self._connected = True
        logger.info("Upstox client connected")
        return True

    async def disconnect(self) -> None:
        self._connected = False
        self._headers = {}

    async def _request(self, method: str, url: str, json_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make an HTTP request to Upstox API."""
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"https://api.upstox.com/v2{url}",
                headers=self._headers,
                json=json_data,
            )
            response.raise_for_status()
            return response.json()

    async def place_order(self, order: OrderRequest) -> OrderResponse:
        if not self._connected:
            return OrderResponse(
                order_id="", status=OrderStatus.REJECTED,
                message="Upstox client not connected",
            )
        try:
            data = {
                "quantity": order.quantity,
                "product": "I",  # Intraday
                "validity": "DAY",
                "price": order.price or 0,
                "instrument_token": f"NSE_EQ|{order.symbol}",
                "order_type": order.order_type.value,
                "transaction_type": order.side.value,
                "disclosed_quantity": 0,
                "trigger_price": 0,
                "is_amo": False,
            }
            response = await self._request("POST", "/order/place", data)
            if response.get("status") == "success":
                return OrderResponse(
                    order_id=response.get("data", {}).get("order_id", ""),
                    status=OrderStatus.PENDING,
                    message="Order placed with Upstox",
                )
            return OrderResponse(
                order_id="", status=OrderStatus.REJECTED,
                message=f"Upstox rejected: {response.get('errors', [])}",
            )
        except Exception as e:
            logger.error("Upstox place_order error: %s", e)
            return OrderResponse(order_id="", status=OrderStatus.REJECTED, message=str(e))

    async def cancel_order(self, order_id: str) -> bool:
        if not self._connected:
            return False
        try:
            await self._request("DELETE", f"/order/cancel?order_id={order_id}")
            return True
        except Exception as e:
            logger.error("Upstox cancel_order error: %s", e)
            return False

    async def get_positions(self) -> list[Position]:
        if not self._connected:
            return []
        try:
            response = await self._request("GET", "/portfolio/short-term-positions")
            data = response.get("data", [])
            if not data:
                return []
            positions = []
            for p in data:
                positions.append(
                    Position(
                        symbol=p.get("trading_symbol", ""),
                        quantity=int(p.get("quantity", 0)),
                        average_price=float(p.get("average_price", 0)),
                        current_price=float(p.get("last_price", 0)),
                        pnl=float(p.get("pnl", 0)),
                    )
                )
            return positions
        except Exception as e:
            logger.error("Upstox get_positions error: %s", e)
            return []

    async def get_quote(self, symbol: str) -> Quote:
        if not self._connected:
            return Quote(symbol=symbol, last_price=0.0)
        try:
            response = await self._request(
                "GET", f"/market-quote/ltp?instrument_key=NSE_EQ|{symbol}"
            )
            data = response.get("data", {})
            if data:
                key = list(data.keys())[0] if data else None
                if key:
                    return Quote(
                        symbol=symbol,
                        last_price=float(data[key].get("last_price", 0)),
                    )
            return Quote(symbol=symbol, last_price=0.0)
        except Exception as e:
            logger.error("Upstox get_quote error: %s", e)
            return Quote(symbol=symbol, last_price=0.0)

    async def get_order_status(self, order_id: str) -> OrderResponse:
        if not self._connected:
            return OrderResponse(
                order_id=order_id, status=OrderStatus.REJECTED, message="Not connected",
            )
        try:
            response = await self._request("GET", f"/order/details?order_id={order_id}")
            data = response.get("data", {})
            if data:
                status_map = {
                    "complete": OrderStatus.EXECUTED,
                    "rejected": OrderStatus.REJECTED,
                    "cancelled": OrderStatus.CANCELLED,
                    "open": OrderStatus.PENDING,
                }
                return OrderResponse(
                    order_id=order_id,
                    status=status_map.get(data.get("status", "").lower(), OrderStatus.PENDING),
                    filled_price=float(data.get("average_price", 0)) or None,
                )
            return OrderResponse(
                order_id=order_id, status=OrderStatus.REJECTED, message="Order not found",
            )
        except Exception as e:
            logger.error("Upstox get_order_status error: %s", e)
            return OrderResponse(order_id=order_id, status=OrderStatus.REJECTED, message=str(e))

    async def refresh_session(self) -> dict[str, str] | None:
        # Implement Upstox token generation logic here
        return None
