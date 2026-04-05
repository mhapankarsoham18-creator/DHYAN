# pyright: reportMissingImports=false, reportAny=false, reportExplicitAny=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

pytestmark = pytest.mark.asyncio


# ── Chart Insight Tests ──────────────────────────────────
async def test_chart_insight_returns_insight_key(async_client: AsyncClient) -> None:
    with patch("app.services.ai_service.nim_client") as mock_nim:
        mock_nim.chat.completions.create = AsyncMock(return_value=_mock_response("RSI is neutral."))
        response = await async_client.post(
            "/api/v1/ai/chart-insight",
            json={
                "symbol": "INFY",
                "rsi": 50.0,
                "price_vs_52w_high": -10.0,
                "price_vs_52w_low": 20.0,
                "trend": "sideways",
            },
        )
    assert response.status_code == 200
    assert "insight" in response.json()


async def test_chart_insight_without_rsi(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/ai/chart-insight",
        json={
            "symbol": "TCS",
            "price_vs_52w_high": -5.0,
            "price_vs_52w_low": 40.0,
            "trend": "uptrend",
        },
    )
    assert response.status_code == 200
    assert "insight" in response.json()


# ── Pattern Explainer Tests ──────────────────────────────
async def test_pattern_explain_returns_explanation(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/ai/pattern-explain",
        json={"pattern_name": "doji", "symbol": "RELIANCE"},
    )
    assert response.status_code == 200
    assert "explanation" in response.json()
    assert len(response.json()["explanation"]) > 0


async def test_pattern_explain_unknown_pattern_fallback(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/ai/pattern-explain",
        json={"pattern_name": "triple_rainbow", "symbol": "HDFC"},
    )
    assert response.status_code == 200
    assert "explanation" in response.json()


# ── Sentiment Tests ──────────────────────────────────────
async def test_sentiment_empty_headlines_returns_neutral(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/ai/sentiment",
        json={"symbol": "INFY", "headlines": []},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "neutral"


async def test_sentiment_with_headlines_returns_result(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/ai/sentiment",
        json={
            "symbol": "RELIANCE",
            "headlines": [
                "Reliance reports record quarterly profits",
                "Jio subscriber growth exceeds expectations",
            ],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert data["sentiment"] in ("positive", "negative", "neutral")


# ── SEBI Sanitizer Tests ─────────────────────────────────
def test_sebi_sanitizer_blocks_buy() -> None:
    from app.services.ai_service import sanitize_response
    result = sanitize_response("You should buy this stock now for guaranteed profits.")
    assert "compliance" in result.lower() or "advisor" in result.lower()


def test_sebi_sanitizer_blocks_sell() -> None:
    from app.services.ai_service import sanitize_response
    result = sanitize_response("I recommend you sell immediately before the price drops.")
    assert "compliance" in result.lower() or "advisor" in result.lower()


def test_sebi_sanitizer_blocks_target_price() -> None:
    from app.services.ai_service import sanitize_response
    result = sanitize_response("The target price for this stock is ₹500.")
    assert "compliance" in result.lower() or "advisor" in result.lower()


def test_sebi_sanitizer_allows_clean_text() -> None:
    from app.services.ai_service import sanitize_response
    clean = "The stock is currently trading near its 52-week low with neutral momentum."
    result = sanitize_response(clean)
    assert result == clean


def test_sebi_sanitizer_blocks_entry_point() -> None:
    from app.services.ai_service import sanitize_response
    result = sanitize_response("This is a good entry point for long-term investors.")
    assert "compliance" in result.lower() or "advisor" in result.lower()


# ── Helper ────────────────────────────────────────────────
class _MockChoice:
    def __init__(self, text: str):
        self.message = type("obj", (object,), {"content": text})()

class _MockCompletion:
    def __init__(self, text: str):
        self.choices = [_MockChoice(text)]

def _mock_response(text: str) -> _MockCompletion:
    return _MockCompletion(text)
