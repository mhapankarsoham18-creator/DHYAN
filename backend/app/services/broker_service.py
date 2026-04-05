"""Broker connection service — manages encrypted token storage and retrieval.

Uses AES-256-GCM + HKDF via TokenEncryption for bank-grade token security.
"""
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.broker_connection import BrokerConnection
from app.services.token_encryption import TokenEncryption

logger = logging.getLogger(__name__)


class BrokerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_connection(
        self,
        user_id: str,
        broker_name: str,
        access_token: str,
        refresh_token: str | None = None,
    ) -> BrokerConnection:
        """Save or update a broker connection with encrypted tokens."""
        encrypted_access = TokenEncryption.encrypt_token(access_token, user_id)
        encrypted_refresh = (
            TokenEncryption.encrypt_token(refresh_token, user_id)
            if refresh_token
            else None
        )

        result = await self.db.execute(
            select(BrokerConnection).where(
                BrokerConnection.user_id == user_id,
                BrokerConnection.broker_name == broker_name,
            )
        )
        connection = result.scalars().first()

        if connection:
            connection.access_token = encrypted_access
            connection.refresh_token = encrypted_refresh
            connection.is_active = True
        else:
            connection = BrokerConnection(
                user_id=user_id,
                broker_name=broker_name,
                access_token=encrypted_access,
                refresh_token=encrypted_refresh,
            )
            self.db.add(connection)

        await self.db.commit()
        logger.info("Broker connection saved for user %s: %s", user_id, broker_name)
        return connection

    async def get_decrypted_tokens(
        self, user_id: str, broker_name: str
    ) -> dict | None:
        """Retrieve and decrypt tokens for an active broker connection."""
        result = await self.db.execute(
            select(BrokerConnection).where(
                BrokerConnection.user_id == user_id,
                BrokerConnection.broker_name == broker_name,
                BrokerConnection.is_active == True,  # noqa: E712
            )
        )
        connection = result.scalars().first()

        if not connection:
            return None

        access_token = TokenEncryption.decrypt_token(
            connection.access_token, user_id
        )
        refresh_token = (
            TokenEncryption.decrypt_token(connection.refresh_token, user_id)
            if connection.refresh_token
            else None
        )

        return {
            "broker_name": broker_name,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def disconnect_broker(self, user_id: str, broker_name: str) -> bool:
        """Disconnect a broker — securely wipe tokens."""
        result = await self.db.execute(
            select(BrokerConnection).where(
                BrokerConnection.user_id == user_id,
                BrokerConnection.broker_name == broker_name,
            )
        )
        connection = result.scalars().first()

        if connection:
            connection.access_token = None
            connection.refresh_token = None
            connection.is_active = False
            await self.db.commit()
            logger.info("Broker %s disconnected for user %s", broker_name, user_id)
            return True
        return False
