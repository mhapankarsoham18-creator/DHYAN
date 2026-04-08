import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import SessionLocal
from app.models.broker_connection import BrokerConnection
from app.services.broker.broker_factory import create_broker_client
from app.services.token_encryption import TokenEncryption

logger = logging.getLogger(__name__)

class TokenRefreshService:
    """Background service to refresh broker session tokens every morning at 08:30 AM IST."""
    
    def __init__(self):
        self.scheduler: AsyncIOScheduler = AsyncIOScheduler()
        
    def start(self):
        # Run daily at 08:30 AM IST (Which is ~03:00 AM UTC, assuming system time is UTC)
        # Using cron trigger
        _ = self.scheduler.add_job(self.refresh_all_active_tokens, 'cron', hour=3, minute=0)
        self.scheduler.start()
        logger.info("Token Refresh Service started. Scheduled daily at 03:00 UTC (08:30 IST).")

    async def refresh_all_active_tokens(self) -> None:
        """Batch job to refresh tokens for all active broker connections."""
        logger.info("Starting daily broker token refresh job...")
        
        # Need to use async context manager for AsyncSession
        async with SessionLocal() as db:
            try:
                stmt = select(BrokerConnection).filter(BrokerConnection.is_active == True)
                result = await db.execute(stmt)
                active_connections = result.scalars().all()
                if not active_connections:
                    logger.info("No active broker connections to refresh.")
                    return

                for conn in active_connections:
                    await self._refresh_single_connection(conn, db)
                    
            except Exception as e:
                logger.error(f"Error in token refresh batch job: {e}")
            finally:
                logger.info("Token refresh job completed.")

    async def _refresh_single_connection(self, conn: BrokerConnection, db: AsyncSession) -> None:
        user_id_str = str(conn.user_id)
        broker_name = conn.broker_name
        
        # 1. Decrypt current tokens
        access_token = TokenEncryption.decrypt_token(conn.access_token, user_id_str) if conn.access_token else None
        refresh_token = TokenEncryption.decrypt_token(conn.refresh_token, user_id_str) if conn.refresh_token else None
        
        # 2. Initialize Broker Client
        broker = create_broker_client(broker_name, access_token=access_token, refresh_token=refresh_token)
        if broker is None:
            logger.warning(f"Unknown broker '{broker_name}' for connection {conn.id}. Skipping.")
            return

        # 3. Request Session Refresh
        try:
            logger.debug(f"Attempting token refresh for user {user_id_str} on broker {broker_name}")
            new_tokens = await broker.refresh_session()
            
            if new_tokens and new_tokens.get("access_token"):
                # 4. Encrypt new tokens
                new_enc_access = TokenEncryption.encrypt_token(new_tokens["access_token"], user_id_str)
                new_enc_refresh = TokenEncryption.encrypt_token(new_tokens.get("refresh_token", ""), user_id_str) if new_tokens.get("refresh_token") else None
                
                # 5. Save back to DB
                conn.access_token = new_enc_access
                if new_enc_refresh:
                    conn.refresh_token = new_enc_refresh
                    
                await db.commit()
                logger.info(f"Successfully refreshed tokens for user {user_id_str} on broker {broker_name}")
            else:
                logger.warning(f"Broker {broker_name} did not return new tokens for user {user_id_str}.")
        except Exception as e:
            logger.error(f"Failed to refresh token for user {user_id_str} on broker {broker_name}: {e}")
            await db.rollback()
