from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.alert import Alert
import logging

logger = logging.getLogger(__name__)

class AlertEngine:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        
    def start(self):
        # Poll every 30 seconds as per phase 2.1
        self.scheduler.add_job(self.poll_prices, 'interval', seconds=30)
        self.scheduler.start()
        logger.info("Alert Engine started with 30s polling interval.")

    async def poll_prices(self):
        db = SessionLocal()
        try:
            active_alerts = db.query(Alert).filter(Alert.is_active == True).all()
            if not active_alerts:
                return

            # Group by symbol to reduce API calls
            symbols = list(set([a.symbol for a in active_alerts]))
            
            # In Phase 2, we use real prices via Angel One free feed (mocked here for logic)
            # In Phase 3, we would call the actual broker service
            current_prices = await self._get_mock_prices(symbols)
            
            for alert in active_alerts:
                current_price = current_prices.get(alert.symbol)
                if current_price:
                    self._evaluate_condition(alert, current_price, db)
                    
        finally:
            db.close()

    async def _get_mock_prices(self, symbols):
        # Placeholder for real price fetching logic from broker service
        import random
        return {s: random.uniform(100, 3000) for s in symbols}

    def _evaluate_condition(self, alert, current_price, db):
        triggered = False
        if alert.condition == "PRICE_ABOVE" and current_price >= alert.target_price:
            triggered = True
        elif alert.condition == "PRICE_BELOW" and current_price <= alert.target_price:
            triggered = True
            
        if triggered:
            logger.info(f"Alert TRIGGERED: {alert.symbol} at {current_price} (Target: {alert.target_price})")
            # In Phase 2.1, we deliver via FCM (mocked)
            self._send_fcm_notification(alert, current_price)
            alert.is_active = False
            db.commit()

    def _send_fcm_notification(self, alert, price):
        # Mock FCM push notification logic
        logger.info(f"FCM Notification sent to User {alert.user_id} for {alert.symbol}")

alert_engine = AlertEngine()
