# pyright: reportMissingImports=false, reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
from datetime import datetime, timezone, timedelta
from app.services.simulation_service import generate_price_series, get_current_simulated_prices, SIM_TICKERS

def test_generate_price_series_creates_data() -> None:
    sim_start = datetime.now(timezone.utc) - timedelta(days=1)
    # Generate 24 hours of data
    series = generate_price_series("user_test", sim_start, "ALPHATECH", 24)
    assert len(series) == 24
    assert series[0]["price"] > 0
    assert series[-1]["price"] > 0

def test_generate_price_series_bounds_at_floor() -> None:
    sim_start = datetime.now(timezone.utc)
    # Force a massive crash by setting volatility extremely high temporarily just for test logic
    # But since sim uses hardcoded tickers, we can just test that no price goes below 1.0
    series = generate_price_series("user_test", sim_start, "NEXAGEN", 1000)
    for point in series:
        assert point["price"] >= 1.0

def test_different_users_get_different_seeds() -> None:
    sim_start = datetime.now(timezone.utc)
    series1 = generate_price_series("userA", sim_start, "VAULTFIN", 10)
    series2 = generate_price_series("userB", sim_start, "VAULTFIN", 10)
    
    # Prices over a 10 hour walk should diverge
    assert series1[-1]["price"] != series2[-1]["price"]

def test_get_current_simulated_prices() -> None:
    sim_start = datetime.now(timezone.utc) - timedelta(hours=5)
    prices = get_current_simulated_prices("user_test", sim_start)
    assert len(prices) == len(SIM_TICKERS)
    
    for p in prices:
        assert "symbol" in p
        assert p["latestPrice"] >= 1.0
        assert "change" in p
        assert "changePercent" in p
