import uuid
import structlog
from typing_extensions import override

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

logger = structlog.get_logger(__name__)


class PaperTradingClient(BrokerInterface):
    """A simulated broker client for paper trading.

    Maintains an in-memory portfolio and executes orders instantly
    at the requested price (or a simulated last price for MARKET orders).
    This allows users to practice trading without risking real money.
    """

    def __init__(self, initial_balance: float = 1_000_000.0):
        self._balance = initial_balance
        self._positions: dict[str, Position] = {}
        self._orders: dict[str, OrderResponse] = {}
        self._connected = False
        # Simulated price cache — in a real implementation this would
        # be fed by a market data service.
        self._simulated_prices: dict[str, float] = {}

    # ── Connection ──────────────────────────────────────────

    @override
    async def connect(self) -> bool:
        """Paper trading is always available."""
        self._connected = True
        logger.info("paper_trading.connected")
        return True

    @override
    async def disconnect(self) -> None:
        self._connected = False
        logger.info("paper_trading.disconnected")

    # ── Orders ──────────────────────────────────────────────

    @override
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        """Simulate order execution.

        MARKET orders fill instantly at the simulated last price.
        LIMIT orders fill instantly if the limit condition is met,
        otherwise they stay PENDING (a real implementation would have
        a price-feed loop to check).
        """
        order_id = str(uuid.uuid4())

        fill_price = self._resolve_fill_price(order)

        if fill_price is None:
            response = OrderResponse(
                order_id=order_id,
                status=OrderStatus.REJECTED,
                message=f"No simulated price available for {order.symbol}",
            )
            self._orders[order_id] = response
            logger.warning("paper_trading.order_rejected", symbol=order.symbol)
            return response

        # Calculate cost / proceeds
        cost = fill_price * order.quantity
        if order.side == OrderSide.BUY:
            if cost > self._balance:
                response = OrderResponse(
                    order_id=order_id,
                    status=OrderStatus.REJECTED,
                    message="Insufficient paper balance",
                )
                self._orders[order_id] = response
                return response
            self._balance -= cost
            self._update_position(order.symbol, order.quantity, fill_price)
        else:  # SELL
            pos = self._positions.get(order.symbol)
            if pos is None or pos.quantity < order.quantity:
                response = OrderResponse(
                    order_id=order_id,
                    status=OrderStatus.REJECTED,
                    message="Insufficient position to sell",
                )
                self._orders[order_id] = response
                return response
            self._balance += cost
            self._update_position(order.symbol, -order.quantity, fill_price)

        response = OrderResponse(
            order_id=order_id,
            status=OrderStatus.EXECUTED,
            filled_price=fill_price,
        )
        self._orders[order_id] = response
        logger.info(
            "paper_trading.order_executed",
            order_id=order_id,
            symbol=order.symbol,
            side=order.side.value,
            qty=order.quantity,
            price=fill_price,
        )
        return response

    @override
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending paper order."""
        order = self._orders.get(order_id)
        if order and order.status == OrderStatus.PENDING:
            order.status = OrderStatus.CANCELLED
            return True
        return False

    @override
    async def get_order_status(self, order_id: str) -> OrderResponse:
        order = self._orders.get(order_id)
        if order is None:
            return OrderResponse(
                order_id=order_id,
                status=OrderStatus.REJECTED,
                message="Order not found",
            )
        return order

    # ── Positions / Quotes ──────────────────────────────────

    @override
    async def get_positions(self) -> list[Position]:
        return list(self._positions.values())

    @override
    async def get_quote(self, symbol: str) -> Quote:
        price = self._simulated_prices.get(symbol, 0.0)
        return Quote(symbol=symbol, last_price=price)

    # ── Public helpers (useful for tests / seeding) ─────────

    def set_simulated_price(self, symbol: str, price: float) -> None:
        """Manually seed a simulated price for a symbol."""
        self._simulated_prices[symbol] = price

    @property
    def balance(self) -> float:
        return self._balance

    # ── Private helpers ─────────────────────────────────────

    def _resolve_fill_price(self, order: OrderRequest) -> float | None:
        if order.order_type == OrderType.MARKET:
            return self._simulated_prices.get(order.symbol)
        else:  # LIMIT
            return order.price

    def _update_position(self, symbol: str, qty_delta: int, price: float) -> None:
        """Update or create position after a fill."""
        pos = self._positions.get(symbol)
        if pos is None:
            self._positions[symbol] = Position(
                symbol=symbol,
                quantity=qty_delta,
                average_price=price,
            )
        else:
            total_qty = pos.quantity + qty_delta
            if total_qty <= 0:
                # Position closed
                self._positions.pop(symbol, None)
            else:
                if qty_delta > 0:
                    # Weighted avg price on buy
                    total_cost = (pos.average_price * pos.quantity) + (price * qty_delta)
                    pos.average_price = total_cost / total_qty
                pos.quantity = total_qty

    @override
    async def refresh_session(self) -> dict[str, str] | None:
        # Paper trading requires no token refresh
        return None
