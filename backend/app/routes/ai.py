from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from app.models.user import User

from app.services.auth_service import get_current_user
from app.services.ai_service import (
    get_chart_insight,
    explain_pattern,
    get_sentiment_summary,
    get_market_weekly_report,
    get_portfolio_weekly_report
)

# Placeholder for slowapi limiter if instantiated historically in a main or dependency module
# For now, we assume a centralized app.state.limiter or similar, or we can use local limiter
# We'll skip @limiter.limit decorators for brevity unless a strict global limiter instance is available.
# In a real app, `from app.core.rate_limit import limiter` would be used.

router = APIRouter(prefix="/ai", tags=["AI"])

# ==========================================
# Pydantic Schemas
# ==========================================
class ChartInsightRequest(BaseModel):
    symbol: str
    rsi: float | None = None
    macd_signal: str | None = None
    price_vs_52w_high: float
    price_vs_52w_low: float
    trend: str

class PatternRequest(BaseModel):
    pattern_name: str
    symbol: str

class SentimentRequest(BaseModel):
    symbol: str
    headlines: list[str]

class MarketReportRequest(BaseModel):
    nifty_change_pct: float
    top_sector: str

class PortfolioReportRequest(BaseModel):
    trades_count: int
    win_rate: float
    pnl_percentage: float

# ==========================================
# Routes
# ==========================================

@router.post("/chart-insight")
async def api_chart_insight(body: ChartInsightRequest, user: User = Depends(get_current_user)):
    insight = await get_chart_insight(
        symbol=body.symbol,
        rsi=body.rsi,
        macd_signal=body.macd_signal,
        price_vs_52w_high=body.price_vs_52w_high,
        price_vs_52w_low=body.price_vs_52w_low,
        trend=body.trend
    )
    return {"insight": insight}

@router.post("/pattern-explain")
async def api_pattern_explain(body: PatternRequest, user: User = Depends(get_current_user)):
    explanation = await explain_pattern(
        pattern_name=body.pattern_name,
        symbol=body.symbol
    )
    return {"explanation": explanation}

@router.post("/sentiment")
async def api_sentiment(body: SentimentRequest, user: User = Depends(get_current_user)):
    # Cap headlines strictly to 5 to prevent token stuffing
    result = await get_sentiment_summary(
        symbol=body.symbol,
        headlines=body.headlines[:5]
    )
    return result

@router.post("/reports/market-weekly")
async def api_market_weekly(body: MarketReportRequest, user: User = Depends(get_current_user)):
    report = await get_market_weekly_report(
        nifty_change_pct=body.nifty_change_pct,
        top_sector=body.top_sector
    )
    return {"report": report}

@router.post("/reports/portfolio-weekly")
async def api_portfolio_weekly(body: PortfolioReportRequest, user: User = Depends(get_current_user)):
    report = await get_portfolio_weekly_report(
        trades_count=body.trades_count,
        win_rate=body.win_rate,
        pnl_percentage=body.pnl_percentage
    )
    return {"report": report}
