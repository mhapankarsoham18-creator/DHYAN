# pyright: reportMissingImports=false, reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportImplicitOverride=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportMissingTypeStubs=false

"""Shoonya (Finvasia) broker client.

Implements BrokerInterface using the NorenRestApiPy SDK.
Requires env vars: SHOONYA_API_KEY, SHOONYA_CLIENT_ID
"""
import os
import logging
from typing import Any

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

API_KEY = os.getenv("SHOONYA_API_KEY")
CLIENT_ID = os.getenv("SHOONYA_CLIENT_ID")


class ShoonyaClient(BrokerInterface):
    """Shoonya (Finvasia) broker integration."""

    def __init__(
        self,
        access_token: str | None = None,
        refresh_token: str | None = None,
    ):
        self._access_token: str | None = access_token
        self._refresh_token: str | None = refresh_token
        self._client: Any = None
        self._connected: bool = False

    async def connect(self) -> bool:
        if not API_KEY or not CLIENT_ID:
            logger.error("Shoonya API keys not configured. Set SHOONYA_API_KEY and SHOONYA_CLIENT_ID in .env")
            return False

        if not self._access_token:
            logger.error("Shoonya access token not provided")
            return False

        try:
            from NorenRestApiPy.NorenApi import NorenApi  # type: ignore

            self._client = NorenApi(
                host="https://api.shoonya.com/NorenWClientTP",
                websocket="wss://api.shoonya.com/NorenWSTP",
            )
            # Set the pre-authenticated session token
            self._client.set_session(
                userid=CLIENT_ID,
                password="",
                usertoken=self._access_token,
            )
            self._connected = True
            logger.info("Shoonya client connected for %s", CLIENT_ID)
            return True
        except ImportError:
            logger.error("NorenRestApiPy not installed. Run: pip install NorenRestApiPy")
            return False
        except Exception as e:
            logger.error("Shoonya connection failed: %s", e)
            return False

    async def disconnect(self) -> None:
        if self._client and self._connected:
            try:
                self._client.logout()
            except Exception as e:
                logger.warning("Shoonya disconnect warning: %s", e)
        self._connected = False
        self._client = None

    async def place_order(self, order: OrderRequest) -> OrderResponse:
        if not self._connected or not self._client:
            return OrderResponse(
                order_id="", status=OrderStatus.REJECTED,
                message="Shoonya client not connected",
            )
        try:
            buy_or_sell = "B" if order.side == OrderSide.BUY else "S"
            prc_type = "MKT" if order.order_type == OrderType.MARKET else "LMT"

            response = self._client.place_order(
                buy_or_sell=buy_or_sell,
                product_type="I",  # Intraday
                exchange="NSE",
                tradingsymbol=order.symbol,
                quantity=order.quantity,
                discloseqty=0,
                price_type=prc_type,
                price=order.price or 0,
                retention="DAY",
            )
            if response and response.get("norenordno"):
                return OrderResponse(
                    order_id=response["norenordno"],
                    status=OrderStatus.PENDING,
                    message="Order placed with Shoonya",
                )
            return OrderResponse(
                order_id="", status=OrderStatus.REJECTED,
                message=f"Shoonya rejected: {response}",
            )
        except Exception as e:
            logger.error("Shoonya place_order error: %s", e)
            return OrderResponse(order_id="", status=OrderStatus.REJECTED, message=str(e))

    async def cancel_order(self, order_id: str) -> bool:
        if not self._connected or not self._client:
            return False
        try:
            self._client.cancel_order(orderno=order_id)
            return True
        except Exception as e:
            logger.error("Shoonya cancel_order error: %s", e)
            return False

    async def get_positions(self) -> list[Position]:
        if not self._connected or not self._client:
            return []
        try:
            response = self._client.get_positions()
            if not response:
                return []
            positions = []
            for p in response:
                positions.append(
                    Position(
                        symbol=p.get("tsym", ""),
                        quantity=int(p.get("netqty", 0)),
                        average_price=float(p.get("netavgprc", 0)),
                        current_price=float(p.get("lp", 0)),
                        pnl=float(p.get("rpnl", 0)),
                    )
                )
            return positions
        except Exception as e:
            logger.error("Shoonya get_positions error: %s", e)
            return []

    async def get_quote(self, symbol: str) -> Quote:
        if not self._connected or not self._client:
            return Quote(symbol=symbol, last_price=0.0)
        try:
            response = self._client.get_quotes(exchange="NSE", token=symbol)
            if response:
                return Quote(
                    symbol=symbol,
                    last_price=float(response.get("lp", 0)),
                    bid=float(response.get("bp1", 0)),
                    ask=float(response.get("sp1", 0)),
                    volume=int(response.get("v", 0)),
                )
            return Quote(symbol=symbol, last_price=0.0)
        except Exception as e:
            logger.error("Shoonya get_quote error: %s", e)
            return Quote(symbol=symbol, last_price=0.0)

    async def get_order_status(self, order_id: str) -> OrderResponse:
        if not self._connected or not self._client:
            return OrderResponse(
                order_id=order_id, status=OrderStatus.REJECTED, message="Not connected",
            )
        try:
            response = self._client.single_order_history(orderno=order_id)
            if response and len(response) > 0:
                latest = response[-1]
                status_map = {
                    "COMPLETE": OrderStatus.EXECUTED,
                    "REJECTED": OrderStatus.REJECTED,
                    "CANCELLED": OrderStatus.CANCELLED,
                    "OPEN": OrderStatus.PENDING,
                }
                return OrderResponse(
                    order_id=order_id,
                    status=status_map.get(latest.get("status", ""), OrderStatus.PENDING),
                    filled_price=float(latest.get("avgprc", 0)) or None,
                )
            return OrderResponse(
                order_id=order_id, status=OrderStatus.REJECTED, message="Order not found",
            )
        except Exception as e:
            logger.error("Shoonya get_order_status error: %s", e)
            return OrderResponse(order_id=order_id, status=OrderStatus.REJECTED, message=str(e))
