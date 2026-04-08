"""
RandomWalkPriceService — Generates unpredictable synthetic market data
for the 7-day practice simulation mode.

Uses Geometric Brownian Motion (GBM) so prices look realistic but are
completely random and cannot be predicted or gamed.
"""
import random
import math
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Any, TypedDict

class SimTicker(TypedDict):
    symbol: str
    base_price: float
    volatility: float

# Simulation universe — fictional tickers so users can't cross-reference
SIM_TICKERS: list[SimTicker] = [
    {"symbol": "ALPHATECH", "base_price": 1250.0, "volatility": 0.025},
    {"symbol": "NEXAGEN",   "base_price": 780.0,  "volatility": 0.030},
    {"symbol": "VAULTFIN",  "base_price": 2100.0, "volatility": 0.020},
    {"symbol": "IRONPEAK",  "base_price": 345.0,  "volatility": 0.035},
    {"symbol": "SOLARCREST", "base_price": 560.0, "volatility": 0.028},
    {"symbol": "QUANTEDGE", "base_price": 1890.0, "volatility": 0.022},
    {"symbol": "DEEPMIND",  "base_price": 4200.0, "volatility": 0.018},
    {"symbol": "NOVABLUE",  "base_price": 920.0,  "volatility": 0.032},
]

SIMULATION_DURATION_DAYS = 7
STARTING_BALANCE = 250000.0


def _user_seed(user_id: str, sim_start: datetime) -> int:
    """Create a unique seed per user+simulation so each run is different."""
    raw = f"{user_id}-{sim_start.isoformat()}"
    return int(hashlib.sha256(raw.encode()).hexdigest()[:12], 16)


def get_simulation_remaining(sim_start: datetime) -> timedelta:
    """How much time is left in the 7-day simulation."""
    end = sim_start + timedelta(days=SIMULATION_DURATION_DAYS)
    remaining = end - datetime.now(timezone.utc)
    return max(remaining, timedelta(0))


def is_simulation_expired(sim_start: datetime) -> bool:
    return get_simulation_remaining(sim_start).total_seconds() <= 0


def generate_price_series(
    user_id: str,
    sim_start: datetime,
    symbol: str,
    num_points: int = 168,  # 1 point per hour for 7 days
) -> list[dict[str, Any]]:
    """
    Generate a deterministic-per-user random walk price series.
    Uses Geometric Brownian Motion: S(t+1) = S(t) * exp((mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z)
    where Z ~ N(0,1).
    """
    ticker = next((t for t in SIM_TICKERS if t["symbol"] == symbol), None)
    if not ticker:
        return []

    seed = _user_seed(user_id, sim_start) + hash(symbol)
    rng = random.Random(seed)

    base = ticker["base_price"]
    sigma = ticker["volatility"]
    mu = 0.0002  # Tiny drift
    dt = 1.0 / 24  # hourly steps

    prices = []
    price = base
    current_time = sim_start

    for i in range(num_points):
        z = rng.gauss(0, 1)
        price = price * math.exp((mu - 0.5 * sigma**2) * dt + sigma * math.sqrt(dt) * z)
        price = max(price, 1.0)  # Floor at ₹1
        prices.append({
            "timestamp": (current_time + timedelta(hours=i)).isoformat(),
            "price": round(price, 2),
        })

    return prices


def get_current_simulated_prices(user_id: str, sim_start: datetime) -> list[dict[str, Any]]:
    """
    Get the CURRENT simulated price for all tickers. 
    Computed from the random walk up to the current moment.
    """
    now = datetime.now(timezone.utc)
    elapsed_hours = int((now - sim_start).total_seconds() / 3600)
    elapsed_hours = max(1, min(elapsed_hours, SIMULATION_DURATION_DAYS * 24))

    results = []
    for ticker in SIM_TICKERS:
        series = generate_price_series(user_id, sim_start, ticker["symbol"], elapsed_hours)
        if len(series) >= 2:
            current = series[-1]["price"]
            prev = series[-2]["price"]
            change = current - prev
            change_pct = (change / prev) * 100 if prev > 0 else 0
        else:
            current = ticker["base_price"]
            change = 0
            change_pct = 0

        results.append({
            "symbol": ticker["symbol"],
            "latestPrice": current,
            "change": round(change, 2),
            "changePercent": round(change_pct, 2),
        })

    return results


def get_simulated_market_overview(user_id: str, sim_start: datetime) -> dict[str, Any]:
    """Full market overview using simulated data."""
    prices = get_current_simulated_prices(user_id, sim_start)

    # Sort for gainers/losers
    sorted_by_change = sorted(prices, key=lambda x: x["changePercent"], reverse=True)
    gainers = [p for p in sorted_by_change if p["changePercent"] > 0][:4]
    losers = list(reversed([p for p in sorted_by_change if p["changePercent"] < 0]))[:4]

    # Create simulated "indices"
    avg_price = sum(p["latestPrice"] for p in prices) / len(prices)
    avg_change = sum(p["change"] for p in prices) / len(prices)

    remaining = get_simulation_remaining(sim_start)
    days_left = remaining.days
    hours_left = remaining.seconds // 3600

    return {
        "is_simulation": True,
        "simulation_remaining": f"{days_left}d {hours_left}h",
        "indices": [
            {
                "symbol": "SIM INDEX",
                "value": round(avg_price * 10, 2),
                "change": round(avg_change * 10, 2),
                "changePercent": round(avg_change / avg_price * 100, 2) if avg_price > 0 else 0,
            }
        ],
        "topGainers": [
            {"symbol": p["symbol"], "value": p["latestPrice"], "change": p["change"], "changePercent": p["changePercent"]}
            for p in gainers
        ],
        "topLosers": [
            {"symbol": p["symbol"], "value": p["latestPrice"], "change": abs(p["change"]), "changePercent": p["changePercent"]}
            for p in losers
        ],
        "activeSectors": [
            {"name": "SIM-Tech", "momentum": random.randint(30, 90)},
            {"name": "SIM-Finance", "momentum": random.randint(30, 90)},
            {"name": "SIM-Energy", "momentum": random.randint(30, 90)},
        ],
    }
