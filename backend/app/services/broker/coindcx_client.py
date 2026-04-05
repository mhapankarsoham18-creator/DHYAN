"""CoinDCX broker client.

Implements BrokerInterface for crypto trading via CoinDCX REST API.
Requires env var: COINDCX_API_KEY
"""
import os
import logging
import hmac
import hashlib
import json
import time
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

API_KEY = os.getenv("COINDCX_API_KEY")
API_SECRET = os.getenv("COINDCX_API_SECRET", "")


class CoinDCXClient(BrokerInterface):
    """CoinDCX crypto exchange integration via REST API."""

    BASE_URL = "https://api.coindcx.com"

    def __init__(
        self,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ):
        # For CoinDCX, access_token is the API key, refresh_token is the secret
        self._api_key = access_token or API_KEY or ""
        self._api_secret = refresh_token or API_SECRET or ""
        self._connected = False

    def _sign(self, payload: dict[str, Any]) -> tuple[str, str]:
        """Create HMAC signature for CoinDCX API."""
        json_body = json.dumps(payload, separators=(",", ":"))
        signature = hmac.new(
            self._api_secret.encode(),
            json_body.encode(),
            hashlib.sha256,
        ).hexdigest()
        return json_body, signature

    async def connect(self) -> bool:
        if not self._api_key or not self._api_secret:
            logger.error(
                "CoinDCX API keys not configured. "
                "Set COINDCX_API_KEY and COINDCX_API_SECRET in .env"
            )
            return False

        try:
            import httpx
            async with httpx.AsyncClient() as client:
                timestamp = int(time.time() * 1000)
                payload = {"timestamp": timestamp}
                body, signature = self._sign(payload)
                response = await client.post(
                    f"{self.BASE_URL}/exchange/v1/users/balances",
                    content=body,
                    headers={
                        "Content-Type": "application/json",
                        "X-AUTH-APIKEY": self._api_key,
                        "X-AUTH-SIGNATURE": signature,
                    },
                )
                if response.status_code == 200:
                    self._connected = True
                    logger.info("CoinDCX client connected")
                    return True
                else:
                    logger.error("CoinDCX auth failed: %s", response.text)
                    return False
        except ImportError:
            logger.error("httpx not installed. Run: pip install httpx")
            return False
        except Exception as e:
            logger.error("CoinDCX connection failed: %s", e)
            return False

    async def disconnect(self) -> None:
        self._connected = False

    async def place_order(self, order: OrderRequest) -> OrderResponse:
        if not self._connected:
            return OrderResponse(
                order_id="", status=OrderStatus.REJECTED,
                message="CoinDCX client not connected",
            )
        try:
            import httpx
            timestamp = int(time.time() * 1000)
            payload: dict[str, Any] = {
                "side": "buy" if order.side == OrderSide.BUY else "sell",
                "order_type": "market_order" if order.order_type == OrderType.MARKET else "limit_order",
                "market": order.symbol,
                "total_quantity": order.quantity,
                "timestamp": timestamp,
            }
            if order.order_type == OrderType.LIMIT and order.price:
                payload["price_per_unit"] = order.price

            body, signature = self._sign(payload)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/exchange/v1/orders/create",
                    content=body,
                    headers={
                        "Content-Type": "application/json",
                        "X-AUTH-APIKEY": self._api_key,
                        "X-AUTH-SIGNATURE": signature,
                    },
                )
                data = response.json()
                if response.status_code == 200 and data.get("id"):
                    return OrderResponse(
                        order_id=data["id"],
                        status=OrderStatus.PENDING,
                        message="Order placed with CoinDCX",
                    )
                return OrderResponse(
                    order_id="", status=OrderStatus.REJECTED,
                    message=f"CoinDCX rejected: {data}",
                )
        except Exception as e:
            logger.error("CoinDCX place_order error: %s", e)
            return OrderResponse(order_id="", status=OrderStatus.REJECTED, message=str(e))

    async def cancel_order(self, order_id: str) -> bool:
        if not self._connected:
            return False
        try:
            import httpx
            timestamp = int(time.time() * 1000)
            payload = {"id": order_id, "timestamp": timestamp}
            body, signature = self._sign(payload)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/exchange/v1/orders/cancel",
                    content=body,
                    headers={
                        "Content-Type": "application/json",
                        "X-AUTH-APIKEY": self._api_key,
                        "X-AUTH-SIGNATURE": signature,
                    },
                )
                return response.status_code == 200
        except Exception as e:
            logger.error("CoinDCX cancel_order error: %s", e)
            return False

    async def get_positions(self) -> list[Position]:
        if not self._connected:
            return []
        try:
            import httpx
            timestamp = int(time.time() * 1000)
            payload = {"timestamp": timestamp}
            body, signature = self._sign(payload)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/exchange/v1/users/balances",
                    content=body,
                    headers={
                        "Content-Type": "application/json",
                        "X-AUTH-APIKEY": self._api_key,
                        "X-AUTH-SIGNATURE": signature,
                    },
                )
                if response.status_code != 200:
                    return []
                data = response.json()
                positions = []
                for b in data:
                    qty = float(b.get("balance", 0))
                    if qty > 0:
                        positions.append(
                            Position(
                                symbol=b.get("currency", ""),
                                quantity=int(qty),
                                average_price=0.0,  # CoinDCX doesn't return avg price in balances
                            )
                        )
                return positions
        except Exception as e:
            logger.error("CoinDCX get_positions error: %s", e)
            return []

    async def get_quote(self, symbol: str) -> Quote:
        """Get quote from CoinDCX public ticker (no auth needed)."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.BASE_URL}/exchange/ticker")
                if response.status_code == 200:
                    for ticker in response.json():
                        if ticker.get("market") == symbol:
                            return Quote(
                                symbol=symbol,
                                last_price=float(ticker.get("last_price", 0)),
                                bid=float(ticker.get("bid", 0)),
                                ask=float(ticker.get("ask", 0)),
                                volume=int(float(ticker.get("volume", 0))),
                            )
            return Quote(symbol=symbol, last_price=0.0)
        except Exception as e:
            logger.error("CoinDCX get_quote error: %s", e)
            return Quote(symbol=symbol, last_price=0.0)

    async def get_order_status(self, order_id: str) -> OrderResponse:
        if not self._connected:
            return OrderResponse(
                order_id=order_id, status=OrderStatus.REJECTED, message="Not connected",
            )
        try:
            import httpx
            timestamp = int(time.time() * 1000)
            payload = {"id": order_id, "timestamp": timestamp}
            body, signature = self._sign(payload)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/exchange/v1/orders/status",
                    content=body,
                    headers={
                        "Content-Type": "application/json",
                        "X-AUTH-APIKEY": self._api_key,
                        "X-AUTH-SIGNATURE": signature,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    status_map = {
                        "open": OrderStatus.PENDING,
                        "partially_filled": OrderStatus.PENDING,
                        "filled": OrderStatus.EXECUTED,
                        "cancelled": OrderStatus.CANCELLED,
                        "rejected": OrderStatus.REJECTED,
                    }
                    return OrderResponse(
                        order_id=order_id,
                        status=status_map.get(data.get("status", ""), OrderStatus.PENDING),
                        filled_price=float(data.get("avg_price", 0)) or None,
                    )
            return OrderResponse(
                order_id=order_id, status=OrderStatus.REJECTED, message="Order not found",
            )
        except Exception as e:
            logger.error("CoinDCX get_order_status error: %s", e)
            return OrderResponse(order_id=order_id, status=OrderStatus.REJECTED, message=str(e))
