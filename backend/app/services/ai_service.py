import os
import json
import logging
import asyncio
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

# --- Configuration ---
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
if not NVIDIA_API_KEY:
    logger.warning("NVIDIA_API_KEY is not set. AI features will fallback to deterministic templates.")

# We use the Mistral-7B-Instruct specifically optimized on NIM
MODEL = "mistralai/mistral-7b-instruct-v0.3"
NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"

nim_client = AsyncOpenAI(
    base_url=NIM_BASE_URL,
    api_key=NVIDIA_API_KEY or "DUMMY_KEY"
)

analyzer = SentimentIntensityAnalyzer()

# --- SEBI Sanitization Filter ---
# Strictly block terms that could be classified as "investment advice" by regulators.
FORBIDDEN_PHRASES = [
    "buy", "sell", "good entry", "target price", "will rise", "will fall",
    "must invest", "strong bullish signal", "strong bearish signal", "recommend",
    "consider buying", "accumulate", "undervalued", "go long", "book profits",
    "short term target", "long term target", "price target", "stop loss",
    "entry point", "exit point", "golden cross", "death cross", "breakout expected",
    "guaranteed return", "sure shot", "multibagger", "10x return", "safe investment",
    "buy on dips", "sell on rallies", "hold for long term", "add more", "reduce position",
    "exit immediately", "buy immediately", "strong buy", "strong sell", "upside potential",
    "downside risk", "profit booking", "wealth creator", "portfolio pick", "time to buy",
    "time to sell", "don't miss", "once in a lifetime", "market outperformer"
]

def sanitize_response(text: str) -> str:
    """Intercepts LLM output and shreds it if any forbidden SEC/SEBI terms are found."""
    text_lower = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in text_lower:
            logger.error(f"SEBI FILTER TRIGGERED: Blocked phrase '{phrase}' in AI response. Shredding output.")
            return "Analysis omitted for compliance. Please consult a registered financial advisor."
    return text.strip()


# =====================================================================
# FEATURE 1: Chart Insight (Math First, LLM second)
# =====================================================================
async def get_chart_insight(
    symbol: str, rsi: Optional[float], macd_signal: Optional[str], 
    price_vs_52w_high: float, price_vs_52w_low: float, trend: str
) -> str:
    # 1. Deterministic Math & Fact Building
    facts = []
    if rsi is not None:
        if rsi < 30:
            facts.append("The stock is currently mathematically oversold.")
        elif rsi > 70:
            facts.append("The stock is currently mathematically overbought.")
        else:
            facts.append("The momentum indicator is neutral.")
            
    if price_vs_52w_high < 5:
        facts.append("The price is trading near its yearly highs.")
    elif price_vs_52w_low < 5:
        facts.append("The price is trading near its yearly lows.")
        
    facts.append(f"The short term trend indicator shows a {trend} trajectory.")

    # Rule-based fallback if no API key or AI fails
    fallback_text = " ".join(facts)
    if not NVIDIA_API_KEY:
        return fallback_text
        
    # 2. NLG (Natural Language Generation) Pass
    prompt = f"""
    You are an AI that ONLY formats text. You do NOT give investment advice.
    Take the following raw facts about {symbol} and combine them into a single, flowing, natural-sounding sentence.
    Do not add any predictions, analysis, or advice.
    FACTS:
    - {' - '.join(facts)}
    """
    try:
        response = await nim_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60,
            temperature=0.1,
            timeout=5.0
        )
        raw_text = response.choices[0].message.content
        return sanitize_response(raw_text)
    except Exception as e:
        logger.warning(f"NIM API failure for Chart Insight: {e}")
        return fallback_text


# =====================================================================
# FEATURE 2: Pattern Explainer
# =====================================================================
PATTERN_DEFINITIONS = {
    "doji": "A Doji forms when open and close prices are nearly equal. It signals market indecision.",
    "hammer": "A Hammer has a long lower wick. It shows that sellers pushed prices down but buyers recovered the close.",
    "engulfing": "An Engulfing pattern features a large candle completely covering the previous candle's body.",
    "morning star": "A Morning Star is a 3-candle pattern indicating a momentum shift from downward to upward.",
    "shooting star": "A Shooting Star has a long upper wick, showing buyers pushed prices up but could not hold."
}

async def explain_pattern(pattern_name: str, symbol: str) -> str:
    p_key = pattern_name.lower()
    base_fact = PATTERN_DEFINITIONS.get(p_key, f"{pattern_name} is a known technical candlestick pattern.")
    
    if not NVIDIA_API_KEY:
        return base_fact

    prompt = f"""
    Rewrite the following textbook definition to sound friendly for a beginner learning about {symbol}.
    Do NOT offer trading advice. Just explain what it visually means.
    DEFINITION: {base_fact}
    """
    try:
        response = await nim_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.2,
            timeout=5.0
        )
        return sanitize_response(response.choices[0].message.content)
    except Exception:
        return base_fact


# =====================================================================
# FEATURE 3: News Sentiment Summarizer
# =====================================================================
async def get_sentiment_summary(symbol: str, headlines: List[str]) -> Dict[str, Any]:
    if not headlines:
        return {"summary": "No recent news found.", "sentiment": "neutral"}

    # 1. Deterministic Sentiment Scoring using Vader locally
    total_score = 0
    for h in headlines:
        score = analyzer.polarity_scores(h)
        total_score += score['compound']
        
    avg_score = total_score / len(headlines)
    sentiment_label = "neutral"
    if avg_score >= 0.15:
        sentiment_label = "positive"
    elif avg_score <= -0.15:
        sentiment_label = "negative"

    # Fallback AI formatting
    fallback_summary = f"Recent news surrounding {symbol} is generally {sentiment_label}."
    
    if not NVIDIA_API_KEY:
         return {"summary": fallback_summary, "sentiment": sentiment_label}

    head_text = "\n".join([f"- {h}" for h in headlines[:5]])
    prompt = f"""
    Read these news headlines for {symbol} and write one plain sentence explaining what the news is about.
    Do not mention the words 'positive', 'negative' or 'sentiment'. Just say what happened.
    HEADLINES:
    {head_text}
    """
    try:
        response = await nim_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.1,
            timeout=5.0
        )
        raw_text = response.choices[0].message.content
        safe_text = sanitize_response(raw_text)
        return {"summary": safe_text, "sentiment": sentiment_label}
    except Exception:
         return {"summary": fallback_summary, "sentiment": sentiment_label}


# =====================================================================
# FEATURE 4: Market Watch Weekly Report
# =====================================================================
async def get_market_weekly_report(nifty_change_pct: float, top_sector: str) -> str:
    facts = f"The NIFTY50 moved by {nifty_change_pct}% this week. The strongest sector was {top_sector}."
    fallback = facts
    if not NVIDIA_API_KEY: return fallback

    prompt = f"""
    Act as a professional newsletter writer. Rewrite these facts into a friendly two-sentence weekly market recap.
    FACTS: {facts}
    """
    try:
        res = await nim_client.chat.completions.create(
            model=MODEL, messages=[{"role": "user", "content": prompt}],
            max_tokens=100, temperature=0.3, timeout=6.0
        )
        return sanitize_response(res.choices[0].message.content)
    except Exception:
        return fallback


# =====================================================================
# FEATURE 5: Personalized Portfolio Report
# =====================================================================
async def get_portfolio_weekly_report(trades_count: int, win_rate: float, pnl_percentage: float) -> str:
    facts = f"You made {trades_count} trades. Your win rate was {win_rate}%. Your portfolio changed by {pnl_percentage}%."
    fallback = f"Your weekly recap: {facts}"
    if not NVIDIA_API_KEY: return fallback

    # Tone changes based on definitive DB math
    tone = "encouraging but cautious" if pnl_percentage < 0 else "congratulatory"

    prompt = f"""
    Write a 2-sentence {tone} weekly recap for a user based on these exact math statistics.
    Do not invent or predict future returns.
    STATS: {facts}
    """
    try:
        res = await nim_client.chat.completions.create(
            model=MODEL, messages=[{"role": "user", "content": prompt}],
            max_tokens=100, temperature=0.2, timeout=6.0
        )
        return sanitize_response(res.choices[0].message.content)
    except Exception:
        return fallback
