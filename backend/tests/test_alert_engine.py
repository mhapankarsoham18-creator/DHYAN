# pyright: reportMissingImports=false, reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
from app.models.alert import Alert
from app.services.alert_engine import AlertEngine

class MockDB:
    def __init__(self):
        self.committed: bool = False
    def commit(self):
        self.committed = True

def test_alert_price_above_triggers() -> None:
    engine = AlertEngine()
    db = MockDB()
    alert = Alert(id=1, user_id=10, symbol="INFY", condition="PRICE_ABOVE", target_price=1500, is_active=True)
    
    # 1500 target. Current 1505 -> should trigger
    engine._evaluate_condition(alert, 1505, db) # pyright: ignore[reportPrivateUsage]
    
    assert db.committed is True
    assert alert.is_active is False

def test_alert_price_above_does_not_trigger() -> None:
    engine = AlertEngine()
    db = MockDB()
    alert = Alert(id=1, user_id=10, symbol="INFY", condition="PRICE_ABOVE", target_price=1500, is_active=True)
    
    # 1500 target. Current 1499 -> should NOT trigger
    engine._evaluate_condition(alert, 1499, db) # pyright: ignore[reportPrivateUsage]
    
    assert db.committed is False
    assert alert.is_active is True

def test_alert_price_below_triggers() -> None:
    engine = AlertEngine()
    db = MockDB()
    alert = Alert(id=1, user_id=10, symbol="INFY", condition="PRICE_BELOW", target_price=1500, is_active=True)
    
    # 1500 target. Current 1490 -> should trigger
    engine._evaluate_condition(alert, 1490, db) # pyright: ignore[reportPrivateUsage]
    
    assert db.committed is True
    assert alert.is_active is False

def test_alert_price_below_does_not_trigger() -> None:
    engine = AlertEngine()
    db = MockDB()
    alert = Alert(id=1, user_id=10, symbol="INFY", condition="PRICE_BELOW", target_price=1500, is_active=True)
    
    # 1500 target. Current 1501 -> should NOT trigger
    engine._evaluate_condition(alert, 1501, db) # pyright: ignore[reportPrivateUsage]
    
    assert db.committed is False
    assert alert.is_active is True
