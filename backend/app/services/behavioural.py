from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.journal import Journal
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class BehaviouralLayer:
    def __init__(self, db: Session):
        self.db = db

    def detect_revenge_trade(self, user_id, current_order):
        # Phase 2.3: Revenge trade detector (tracks loss -> rapid trade pattern)
        # Check for losses in the last 15 minutes and rapid order placement
        time_threshold = datetime.utcnow() - timedelta(minutes=15)
        
        # In Phase 2, we mock the loss detection (would require real portfolio sync in Phase 3)
        # For logic, we look for recent REJECTED or CANCELLED orders in the same symbol
        recent_orders = self.db.query(Order).filter(
            Order.user_id == user_id,
            Order.symbol == current_order.symbol,
            Order.created_at >= time_threshold
        ).all()
        
        if len(recent_orders) >= 3:
            logger.warning(f"Revenge Trade Detected for User {user_id} on {current_order.symbol}")
            return True # Trigger revenge trade warning card
        return False

    def create_journal_entry(self, user_id, notes, tags=None, order_id=None):
        # Phase 2.3: End-of-day journal prompt (emotion picker + text field)
        new_journal = Journal(
            user_id=user_id,
            notes=notes,
            tags=tags,
            order_id=order_id
        )
        self.db.add(new_journal)
        self.db.commit()
        self.db.refresh(new_journal)
        logger.info(f"Journal entry created for User {user_id}")
        return new_journal

    def get_weekly_report_data(self, user_id):
        # Phase 2.5: Backend job generates weekly summary every Sunday 7 PM IST
        # Stats: trades count, win rate, best trade, worst trade, total P&L
        start_of_week = datetime.utcnow() - timedelta(days=7)
        
        orders = self.db.query(Order).filter(
            Order.user_id == user_id,
            Order.created_at >= start_of_week,
            Order.status == "EXECUTED"
        ).all()
        
        # Calculate stats (mocked logic for Phase 2)
        count = len(orders)
        win_rate = 0.65 if count > 0 else 0 # Mock
        total_pnl = sum([o.quantity * 1.5 for o in orders]) # Mock P&L calculation
        
        return {
            "trades_count": count,
            "win_rate": f"{win_rate * 100}%",
            "best_trade": "RELIANCE (+₹450)",
            "worst_trade": "INFY (-₹120)",
            "total_pnl": f"₹{total_pnl:.2f}",
            "narrative": "You stayed disciplined with Reliance but showed slight impatience with Infosys."
        }

    def calculate_tax_pnl(self, user_id, financial_year):
        # Phase 4.3: Annual P&L calculation (STCG, LTCG, speculative income)
        # STCG: Short Term Capital Gains (Holdings < 1 year)
        # LTCG: Long Term Capital Gains (Holdings > 1 year)
        # Speculative: Intraday trades
        
        # Mock calculation logic for Phase 4
        return {
            "financial_year": financial_year,
            "stcg": "₹12,450.00",
            "ltcg": "₹45,200.00",
            "speculative_income": "₹3,120.00",
            "total_tax_liability": "₹7,210.00",
            "status": "Ready for Download (PDF)"
        }
