# pyright: reportMissingImports=false, reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportImplicitOverride=false, reportUnknownVariableType=false, reportUnknownArgumentType=false

"""AngelOne (SmartAPI) broker client.

Implements BrokerInterface using the smartapi-python SDK.
Requires env vars: ANGEL_ONE_API_KEY, ANGEL_ONE_CLIENT_ID
"""
import os
import logging
from typing import Any

from app.services.broker.interface import (
    BrokerInterface,
    OrderRequest,
    OrderResponse,
    OrderStatus,
    Position,
    Quote,
)

logger = logging.getLogger(__name__)

API_KEY = os.getenv("ANGEL_ONE_API_KEY")
CLIENT_ID = os.getenv("ANGEL_ONE_CLIENT_ID")


class AngelOneClient(BrokerInterface):
    """AngelOne SmartAPI broker integration.

    Requires API key and client ID from environment variables.
    Access token is injected from encrypted DB storage.
    """

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
            logger.error("AngelOne API keys not configured. Set ANGEL_ONE_API_KEY and ANGEL_ONE_CLIENT_ID in .env")
            return False

        if not self._access_token:
            logger.error("AngelOne access token not provided — user must authenticate first")
            return False

        try:
            from SmartApi import SmartConnect  # type: ignore
            self._client = SmartConnect(api_key=API_KEY)
            self._client.setAccessToken(self._access_token)
            if self._refresh_token:
                self._client.setRefreshToken(self._refresh_token)
            self._connected = True
            logger.info("AngelOne client connected for client %s", CLIENT_ID)
            return True
        except ImportError:
            logger.error("smartapi-python package not installed. Run: pip install smartapi-python")
            return False
        except Exception as e:
            logger.error("AngelOne connection failed: %s", e)
            return False

    async def disconnect(self) -> None:
        if self._client and self._connected:
            try:
                self._client.terminateSession(CLIENT_ID)
            except Exception as e:
                logger.warning("AngelOne disconnect warning: %s", e)
        self._connected = False
        self._client = None
        logger.info("AngelOne client disconnected")

    async def place_order(self, order: OrderRequest) -> OrderResponse:
        if not self._connected or not self._client:
            return OrderResponse(
                order_id="",
                status=OrderStatus.REJECTED,
                message="AngelOne client not connected",
            )

        try:
            params = {
                "variety": "NORMAL",
                "tradingsymbol": order.symbol,
                "symboltoken": "",  # Looked up via search API in production
                "transactiontype": order.side.value,
                "exchange": "NSE",
                "ordertype": order.order_type.value,
                "producttype": "INTRADAY",
                "duration": "DAY",
                "quantity": str(order.quantity),
                "price": str(order.price or 0),
            }
            response = self._client.placeOrder(params)

            if response and response.get("orderid"):
                return OrderResponse(
                    order_id=response["orderid"],
                    status=OrderStatus.PENDING,
                    message="Order placed with AngelOne",
                )
            else:
                return OrderResponse(
                    order_id="",
                    status=OrderStatus.REJECTED,
                    message=f"AngelOne rejected: {response}",
                )
        except Exception as e:
            logger.error("AngelOne place_order error: %s", e)
            return OrderResponse(
                order_id="",
                status=OrderStatus.REJECTED,
                message=str(e),
            )

    async def cancel_order(self, order_id: str) -> bool:
        if not self._connected or not self._client:
            return False
        try:
            params = {"variety": "NORMAL", "orderid": order_id}
            self._client.cancelOrder(params)
            return True
        except Exception as e:
            logger.error("AngelOne cancel_order error: %s", e)
            return False

    async def get_positions(self) -> list[Position]:
        if not self._connected or not self._client:
            return []
        try:
            response = self._client.position()
            if not response or not response.get("data"):
                return []
            positions = []
            for p in response["data"]:
                positions.append(
                    Position(
                        symbol=p.get("tradingsymbol", ""),
                        quantity=int(p.get("netqty", 0)),
                        average_price=float(p.get("averageprice", 0)),
                        current_price=float(p.get("ltp", 0)),
                        pnl=float(p.get("pnl", 0)),
                    )
                )
            return positions
        except Exception as e:
            logger.error("AngelOne get_positions error: %s", e)
            return []

    async def get_quote(self, symbol: str) -> Quote:
        if not self._connected or not self._client:
            return Quote(symbol=symbol, last_price=0.0)
        try:
            params = {"exchange": "NSE", "tradingsymbol": symbol}
            response = self._client.ltpData(**params)
            if response and response.get("data"):
                data = response["data"]
                return Quote(
                    symbol=symbol,
                    last_price=float(data.get("ltp", 0)),
                )
            return Quote(symbol=symbol, last_price=0.0)
        except Exception as e:
            logger.error("AngelOne get_quote error: %s", e)
            return Quote(symbol=symbol, last_price=0.0)

    async def get_order_status(self, order_id: str) -> OrderResponse:
        if not self._connected or not self._client:
            return OrderResponse(
                order_id=order_id,
                status=OrderStatus.REJECTED,
                message="Not connected",
            )
        try:
            response = self._client.orderBook()
            if response and response.get("data"):
                for o in response["data"]:
                    if o.get("orderid") == order_id:
                        status_map = {
                            "complete": OrderStatus.EXECUTED,
                            "rejected": OrderStatus.REJECTED,
                            "cancelled": OrderStatus.CANCELLED,
                            "open": OrderStatus.PENDING,
                        }
                        return OrderResponse(
                            order_id=order_id,
                            status=status_map.get(
                                o.get("status", "").lower(),
                                OrderStatus.PENDING,
                            ),
                            filled_price=float(o.get("averageprice", 0)) or None,
                        )
            return OrderResponse(
                order_id=order_id,
                status=OrderStatus.REJECTED,
                message="Order not found",
            )
        except Exception as e:
            logger.error("AngelOne get_order_status error: %s", e)
            return OrderResponse(
                order_id=order_id,
                status=OrderStatus.REJECTED,
                message=str(e),
            )

    async def refresh_session(self) -> dict[str, str] | None:
        # Implement AngelOne token generation logic here
        return None
