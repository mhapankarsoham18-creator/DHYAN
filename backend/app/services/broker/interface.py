from abc import ABC, abstractmethod
# No typing imports needed for None pipe operator in Python 3.10
from dataclasses import dataclass
from enum import Enum


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


@dataclass
class OrderRequest:
    """Represents an incoming order placement request."""
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: float | None = None  # Required for LIMIT, ignored for MARKET


@dataclass
class OrderResponse:
    """Represents the broker's response after placing an order."""
    order_id: str
    status: OrderStatus
    filled_price: float | None = None
    message: str | None = None


@dataclass
class Position:
    """Represents a current holding / open position."""
    symbol: str
    quantity: int
    average_price: float
    current_price: float | None = None
    pnl: float | None = None


@dataclass
class Quote:
    """Represents a market quote for a symbol."""
    symbol: str
    last_price: float
    bid: float | None = None
    ask: float | None = None
    volume: int | None = None


class BrokerInterface(ABC):
    """Abstract Base Class defining the contract for all broker integrations.

    All broker clients (Fyers, Paper Trading, etc.) must implement this
    interface to ensure they can be used interchangeably via the Strategy pattern.
    """

    @abstractmethod
    async def connect(self) -> bool:
        """Authenticate and establish connection to the broker.

        Returns:
            True if the connection was successful, False otherwise.
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Gracefully close the broker connection."""
        ...

    @abstractmethod
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        """Place a new order with the broker.

        Args:
            order: The order details to submit.

        Returns:
            An OrderResponse indicating the result.
        """
        ...

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing pending order.

        Args:
            order_id: The broker-assigned order ID to cancel.

        Returns:
            True if cancellation was successful.
        """
        ...

    @abstractmethod
    async def get_positions(self) -> list[Position]:
        """Retrieve all open positions.

        Returns:
            A list of current positions.
        """
        ...

    @abstractmethod
    async def get_quote(self, symbol: str) -> Quote:
        """Get the latest market quote for a given symbol.

        Args:
            symbol: The trading symbol (e.g., 'NSE:RELIANCE').

        Returns:
            A Quote object with the latest price data.
        """
        ...

    @abstractmethod
    async def get_order_status(self, order_id: str) -> OrderResponse:
        """Check the current status of a placed order.

        Args:
            order_id: The broker-assigned order ID.

        Returns:
            An OrderResponse with the current status.
        """
        ...

    @abstractmethod
    async def refresh_session(self) -> dict[str, str] | None:
        """Attempt to refresh an expired access token using the stored refresh_token.
        
        Returns:
            A dict containing new token keys (e.g. {'access_token': 'atk', 'refresh_token': 'rtk'}),
            or None if refresh failed or is unsupported.
        """
        ...
