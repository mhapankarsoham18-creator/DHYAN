"""Broker Factory — returns the correct BrokerInterface based on broker name.

All broker clients read API keys from environment variables.
If keys are missing, the client's connect() method returns False.
"""
import logging
from typing import Optional

from app.services.broker.interface import BrokerInterface
from app.services.broker.paper_client import PaperTradingClient
from app.services.broker.angelone_client import AngelOneClient
from app.services.broker.shoonya_client import ShoonyaClient
from app.services.broker.fyers_client import FyersClient
from app.services.broker.upstox_client import UpstoxClient
from app.services.broker.coindcx_client import CoinDCXClient

logger = logging.getLogger(__name__)

# Registry of supported brokers
_BROKER_MAP: dict[str, type[BrokerInterface]] = {
    "paper": PaperTradingClient,
    "angelone": AngelOneClient,
    "shoonya": ShoonyaClient,
    "fyers": FyersClient,
    "upstox": UpstoxClient,
    "coindcx": CoinDCXClient,
}


def get_supported_brokers() -> list[str]:
    """Return list of supported broker names."""
    return list(_BROKER_MAP.keys())


def create_broker_client(
    broker_name: str,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> Optional[BrokerInterface]:
    """Create a broker client instance.

    Args:
        broker_name: Name of the broker (e.g. 'angelone', 'paper')
        access_token: Decrypted access token from DB (not needed for paper)
        refresh_token: Decrypted refresh token from DB (optional)

    Returns:
        A BrokerInterface instance, or None if broker_name is unknown.
    """
    broker_name = broker_name.lower().strip()

    client_class = _BROKER_MAP.get(broker_name)
    if client_class is None:
        logger.warning("Unknown broker: %s", broker_name)
        return None

    if broker_name == "paper":
        return PaperTradingClient()

    # For real brokers, inject the access token
    return client_class(access_token=access_token, refresh_token=refresh_token)
