"""Fyers broker client.

Implements BrokerInterface using the fyers-apiv3 SDK.
Requires env vars: FYERS_CLIENT_ID, FYERS_SECRET_KEY
"""
import os
import logging
from typing import Optional

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

CLIENT_ID = os.getenv("FYERS_CLIENT_ID")
SECRET_KEY = os.getenv("FYERS_SECRET_KEY")


class FyersClient(BrokerInterface):
    """Fyers broker integration."""

    def __init__(
        self,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ):
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._client = None
        self._connected = False

    async def connect(self) -> bool:
        if not CLIENT_ID or not SECRET_KEY:
            logger.error(
                "Fyers API keys not configured. "
                "Set FYERS_CLIENT_ID and FYERS_SECRET_KEY in .env"
            )
            return False

        if not self._access_token:
            logger.error("Fyers access token not provided")
            return False

        try:
            from fyers_apiv3 import fyersModel

            self._client = fyersModel.FyersModel(
                client_id=CLIENT_ID,
                token=self._access_token,
                is_async=False,
                log_path="",
            )
            # Verify connection with a profile call
            profile = self._client.get_profile()
            if profile.get("s") == "ok":
                self._connected = True
                logger.info("Fyers client connected")
                return True
            else:
                logger.error("Fyers auth failed: %s", profile.get("message"))
                return False
        except ImportError:
            logger.error("fyers-apiv3 not installed. Run: pip install fyers-apiv3")
            return False
        except Exception as e:
            logger.error("Fyers connection failed: %s", e)
            return False

    async def disconnect(self) -> None:
        self._connected = False
        self._client = None

    async def place_order(self, order: OrderRequest) -> OrderResponse:
        if not self._connected or not self._client:
            return OrderResponse(
                order_id="", status=OrderStatus.REJECTED,
                message="Fyers client not connected",
            )
        try:
            data = {
                "symbol": f"NSE:{order.symbol}-EQ",
                "qty": order.quantity,
                "type": 2 if order.order_type == OrderType.MARKET else 1,
                "side": 1 if order.side == OrderSide.BUY else -1,
                "productType": "INTRADAY",
                "limitPrice": order.price or 0,
                "stopPrice": 0,
                "validity": "DAY",
                "offlineOrder": False,
            }
            response = self._client.place_order(data=data)
            if response.get("s") == "ok":
                return OrderResponse(
                    order_id=response.get("id", ""),
                    status=OrderStatus.PENDING,
                    message="Order placed with Fyers",
                )
            return OrderResponse(
                order_id="", status=OrderStatus.REJECTED,
                message=f"Fyers rejected: {response.get('message', '')}",
            )
        except Exception as e:
            logger.error("Fyers place_order error: %s", e)
            return OrderResponse(order_id="", status=OrderStatus.REJECTED, message=str(e))

    async def cancel_order(self, order_id: str) -> bool:
        if not self._connected or not self._client:
            return False
        try:
            data = {"id": order_id}
            response = self._client.cancel_order(data=data)
            return response.get("s") == "ok"
        except Exception as e:
            logger.error("Fyers cancel_order error: %s", e)
            return False

    async def get_positions(self) -> list[Position]:
        if not self._connected or not self._client:
            return []
        try:
            response = self._client.positions()
            if response.get("s") != "ok" or not response.get("netPositions"):
                return []
            positions = []
            for p in response["netPositions"]:
                positions.append(
                    Position(
                        symbol=p.get("symbol", "").split(":")[-1].replace("-EQ", ""),
                        quantity=int(p.get("netQty", 0)),
                        average_price=float(p.get("avgPrice", 0)),
                        current_price=float(p.get("ltp", 0)),
                        pnl=float(p.get("pl", 0)),
                    )
                )
            return positions
        except Exception as e:
            logger.error("Fyers get_positions error: %s", e)
            return []

    async def get_quote(self, symbol: str) -> Quote:
        if not self._connected or not self._client:
            return Quote(symbol=symbol, last_price=0.0)
        try:
            data = {"symbols": f"NSE:{symbol}-EQ"}
            response = self._client.quotes(data=data)
            if response.get("s") == "ok" and response.get("d"):
                d = response["d"][0]["v"]
                return Quote(
                    symbol=symbol,
                    last_price=float(d.get("lp", 0)),
                    bid=float(d.get("bid", 0)),
                    ask=float(d.get("ask", 0)),
                    volume=int(d.get("volume", 0)),
                )
            return Quote(symbol=symbol, last_price=0.0)
        except Exception as e:
            logger.error("Fyers get_quote error: %s", e)
            return Quote(symbol=symbol, last_price=0.0)

    async def get_order_status(self, order_id: str) -> OrderResponse:
        if not self._connected or not self._client:
            return OrderResponse(
                order_id=order_id, status=OrderStatus.REJECTED, message="Not connected",
            )
        try:
            data = {"id": order_id}
            response = self._client.orderBook(data=data)
            if response.get("s") == "ok" and response.get("orderBook"):
                for o in response["orderBook"]:
                    if o.get("id") == order_id:
                        status_map = {
                            2: OrderStatus.EXECUTED,
                            1: OrderStatus.CANCELLED,
                            5: OrderStatus.REJECTED,
                            6: OrderStatus.PENDING,
                        }
                        return OrderResponse(
                            order_id=order_id,
                            status=status_map.get(o.get("status", 6), OrderStatus.PENDING),
                            filled_price=float(o.get("tradedPrice", 0)) or None,
                        )
            return OrderResponse(
                order_id=order_id, status=OrderStatus.REJECTED, message="Order not found",
            )
        except Exception as e:
            logger.error("Fyers get_order_status error: %s", e)
            return OrderResponse(order_id=order_id, status=OrderStatus.REJECTED, message=str(e))

    async def refresh_session(self) -> dict[str, str] | None:
        # Implement Fyers token generation logic here
        return None
