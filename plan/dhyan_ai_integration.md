# Dhyan — AI Integration Plan (NVIDIA NIM)
**Feature:** AI Analysis Assistant  
**Models:** NVIDIA NIM (Mistral 7B primary)  
**Legal frame:** Analysis only — never prediction, never buy/sell advice

---

## What We're Building — 3 AI Features

```
┌─────────────────────────────────────────────────────┐
│                  AI ASSISTANT                        │
│                                                      │
│  1. Chart Insight Line                               │
│     "RSI is oversold. Stock near 52w low."           │
│                                                      │
│  2. Pattern Explainer                                │
│     User taps candlestick pattern → plain explanation│
│                                                      │
│  3. News Sentiment Summary                           │
│     3 headlines → "Overall: cautiously positive"     │
└─────────────────────────────────────────────────────┘
```

---

## Architecture

```
Flutter App
    │
    │  HTTP POST /ai/chart-insight
    │  HTTP POST /ai/pattern-explain  
    │  HTTP POST /ai/sentiment
    │
    ▼
FastAPI Backend (ai_service.py)
    │
    │  OpenAI-compatible API call
    │  base_url = integrate.api.nvidia.com/v1
    │
    ▼
NVIDIA NIM
    │  mistralai/mistral-7b-instruct-v0.3
    ▼
Response → sanitized → returned to Flutter
```

---

## Phase 1 — Backend AI Service

### File: `backend/services/ai_service.py`

```python
import os
from openai import AsyncOpenAI
from typing import Optional
import structlog

log = structlog.get_logger()

nim_client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ["NVIDIA_NIM_API_KEY"]
)

MODEL = "mistralai/mistral-7b-instruct-v0.3"

# ─── Safety wrapper ───────────────────────────────────────
# Strips any buy/sell/prediction language before returning
FORBIDDEN_PHRASES = [
    "buy", "sell", "will go up", "will go down",
    "price target", "recommend", "invest now",
    "guaranteed", "profit", "should purchase"
]

def sanitize_response(text: str) -> str:
    text_lower = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in text_lower:
            return (
                "Analysis unavailable for this data. "
                "Please review the chart manually."
            )
    return text.strip()


# ─── Feature 1: Chart Insight Line ────────────────────────
async def get_chart_insight(
    symbol: str,
    rsi: Optional[float],
    macd_signal: Optional[str],   # "bullish_cross" | "bearish_cross" | "neutral"
    price_vs_52w_high: float,     # percentage below 52w high e.g. -15.3
    price_vs_52w_low: float,      # percentage above 52w low e.g. +8.2
    trend: str,                   # "uptrend" | "downtrend" | "sideways"
    volume_vs_avg: float,         # e.g. 1.4 = 40% above average
) -> str:
    prompt = f"""
You are a calm, educational trading assistant for Indian retail investors with no finance background.
Analyse this technical data and write ONE plain-language insight in maximum 2 sentences.

Rules:
- Never say buy, sell, or predict price movement
- Never give investment advice
- Use simple English, no jargon
- Be factual, not emotional
- If data is unclear, say so honestly

Stock: {symbol}
RSI: {rsi if rsi else 'unavailable'}
MACD: {macd_signal if macd_signal else 'unavailable'}
Price vs 52-week high: {price_vs_52w_high:.1f}%
Price vs 52-week low: {price_vs_52w_low:.1f}%
Current trend: {trend}
Volume vs average: {volume_vs_avg:.1f}x

Write your 2-sentence insight now:
"""

    try:
        response = await nim_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.2,  # low = consistent, factual
            timeout=5.0        # never let AI slow down the UI
        )
        raw = response.choices[0].message.content
        return sanitize_response(raw)

    except Exception as e:
        log.warning("chart_insight_failed", error=str(e))
        return _rule_based_chart_insight(rsi, price_vs_52w_low, trend)


# ─── Rule-based fallback (no API needed) ──────────────────
# Used when NIM is slow or quota exceeded
def _rule_based_chart_insight(
    rsi: Optional[float],
    price_vs_52w_low: float,
    trend: str
) -> str:
    parts = []

    if rsi is not None:
        if rsi < 30:
            parts.append("RSI is in oversold territory (below 30).")
        elif rsi > 70:
            parts.append("RSI is in overbought territory (above 70).")
        else:
            parts.append(f"RSI is neutral at {rsi:.0f}.")

    if price_vs_52w_low < 10:
        parts.append("Price is near its 52-week low.")
    elif price_vs_52w_low > 80:
        parts.append("Price is near its 52-week high.")

    if trend == "uptrend":
        parts.append("Short-term trend is upward.")
    elif trend == "downtrend":
        parts.append("Short-term trend is downward.")

    return " ".join(parts[:2]) if parts else "Insufficient data for analysis."


# ─── Feature 2: Pattern Explainer ─────────────────────────
PATTERN_CACHE: dict[str, str] = {}  # simple in-memory cache

async def explain_pattern(pattern_name: str, symbol: str) -> str:
    # Check cache first — pattern explanations don't change
    cache_key = pattern_name.lower().replace(" ", "_")
    if cache_key in PATTERN_CACHE:
        return PATTERN_CACHE[cache_key]

    prompt = f"""
You are a plain-language trading education assistant for Indian retail investors.
Explain this candlestick pattern in exactly 3 short sentences:
1. What it looks like on a chart (visual description)
2. What it historically means (not a prediction)
3. What traders typically watch for after this pattern

Pattern: {pattern_name}
Stock context: {symbol}

Rules:
- No buy/sell advice
- No price predictions  
- Simple English only
- Maximum 60 words total
"""

    try:
        response = await nim_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.1,
            timeout=5.0
        )
        result = sanitize_response(response.choices[0].message.content)
        PATTERN_CACHE[cache_key] = result  # cache for session
        return result

    except Exception as e:
        log.warning("pattern_explain_failed", error=str(e))
        return PATTERN_DESCRIPTIONS.get(
            pattern_name.lower(),
            f"{pattern_name} is a candlestick pattern. Refer to a charting guide for details."
        )


# ─── Hardcoded fallbacks for common patterns ──────────────
PATTERN_DESCRIPTIONS = {
    "doji": "A Doji forms when open and close prices are nearly equal, creating a cross shape. It signals indecision between buyers and sellers. Traders watch for the next candle's direction as confirmation.",
    "hammer": "A Hammer has a small body at the top with a long lower wick. It appears after a downtrend and shows sellers pushed prices down but buyers recovered. The wick should be at least twice the body length.",
    "engulfing": "A Bullish Engulfing is a large green candle that completely covers the previous red candle. It shows buyers overcame sellers strongly. Traders watch for volume confirmation alongside this pattern.",
    "morning star": "A Morning Star is a 3-candle pattern: red, small middle, then green. It appears after downtrends and shows a shift from selling to buying pressure. The middle candle gaps are important.",
    "shooting star": "A Shooting Star has a small body at the bottom with a long upper wick. It appears after an uptrend and shows buyers pushed prices up but sellers took control. Opposite of a Hammer.",
}


# ─── Feature 3: News Sentiment Summary ────────────────────
async def get_sentiment_summary(
    symbol: str,
    company_name: str,
    headlines: list[str]        # max 5 headlines
) -> dict:
    if not headlines:
        return {
            "summary": "No recent news found for this stock.",
            "sentiment": "neutral",
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0
        }

    headlines_text = "\n".join(
        [f"- {h}" for h in headlines[:5]]  # cap at 5
    )

    prompt = f"""
You are a news analyst for Indian retail investors.
Analyse these headlines about {company_name} ({symbol}).

Headlines:
{headlines_text}

Respond in this exact JSON format (nothing else):
{{
  "summary": "One sentence plain-language summary of overall news tone",
  "sentiment": "positive" or "negative" or "neutral" or "mixed",
  "positive_count": number,
  "negative_count": number,
  "neutral_count": number
}}

Rules:
- No buy/sell advice
- No price predictions
- Be objective and factual
- summary must be under 20 words
"""

    try:
        response = await nim_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.1,
            timeout=6.0
        )
        import json
        raw = response.choices[0].message.content.strip()
        # Extract JSON even if model adds extra text
        start = raw.find("{")
        end = raw.rfind("}") + 1
        parsed = json.loads(raw[start:end])
        parsed["summary"] = sanitize_response(parsed.get("summary", ""))
        return parsed

    except Exception as e:
        log.warning("sentiment_failed", error=str(e))
        return {
            "summary": "Unable to analyse news at this time.",
            "sentiment": "neutral",
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0
        }
```

---

## Phase 2 — FastAPI Routes

### File: `backend/routers/ai.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, validator
from typing import Optional
from slowapi import Limiter
from services.ai_service import (
    get_chart_insight,
    explain_pattern,
    get_sentiment_summary
)
from dependencies import verify_token

router = APIRouter(prefix="/ai", tags=["AI"])
limiter = Limiter(...)

# ─── Request Models ────────────────────────────────────────
class ChartInsightRequest(BaseModel):
    symbol: str
    rsi: Optional[float] = None
    macd_signal: Optional[str] = None
    price_vs_52w_high: float
    price_vs_52w_low: float
    trend: str
    volume_vs_avg: float = 1.0

    @validator("symbol")
    def symbol_valid(cls, v):
        if not v.isalpha() or len(v) > 20:
            raise ValueError("Invalid symbol")
        return v.upper()

    @validator("trend")
    def trend_valid(cls, v):
        if v not in ["uptrend", "downtrend", "sideways"]:
            raise ValueError("Invalid trend")
        return v

class PatternRequest(BaseModel):
    pattern_name: str
    symbol: str

class SentimentRequest(BaseModel):
    symbol: str
    company_name: str
    headlines: list[str]

    @validator("headlines")
    def limit_headlines(cls, v):
        return v[:5]  # hard cap at 5

# ─── Endpoints ─────────────────────────────────────────────
@router.post("/chart-insight")
@limiter.limit("20/minute")   # per user, generous for real-time
async def chart_insight(
    body: ChartInsightRequest,
    user=Depends(verify_token)
):
    insight = await get_chart_insight(
        symbol=body.symbol,
        rsi=body.rsi,
        macd_signal=body.macd_signal,
        price_vs_52w_high=body.price_vs_52w_high,
        price_vs_52w_low=body.price_vs_52w_low,
        trend=body.trend,
        volume_vs_avg=body.volume_vs_avg
    )
    return {"insight": insight}


@router.post("/pattern-explain")
@limiter.limit("10/minute")
async def pattern_explain(
    body: PatternRequest,
    user=Depends(verify_token)
):
    explanation = await explain_pattern(
        pattern_name=body.pattern_name,
        symbol=body.symbol
    )
    return {"explanation": explanation}


@router.post("/sentiment")
@limiter.limit("10/minute")
async def sentiment(
    body: SentimentRequest,
    user=Depends(verify_token)
):
    result = await get_sentiment_summary(
        symbol=body.symbol,
        company_name=body.company_name,
        headlines=body.headlines
    )
    return result
```

---

## Phase 3 — Flutter Integration

### File: `lib/core/services/ai_service.dart`

```dart
import 'package:dio/dio.dart';

class AiService {
  final Dio _dio;
  AiService(this._dio);

  // ── Feature 1: Chart Insight ──────────────────────────
  Future<String> getChartInsight({
    required String symbol,
    double? rsi,
    String? macdSignal,
    required double priceVs52wHigh,
    required double priceVs52wLow,
    required String trend,
    double volumeVsAvg = 1.0,
  }) async {
    try {
      final response = await _dio.post(
        '/ai/chart-insight',
        data: {
          'symbol': symbol,
          'rsi': rsi,
          'macd_signal': macdSignal,
          'price_vs_52w_high': priceVs52wHigh,
          'price_vs_52w_low': priceVs52wLow,
          'trend': trend,
          'volume_vs_avg': volumeVsAvg,
        },
      ).timeout(const Duration(seconds: 6));
      return response.data['insight'] as String;
    } catch (_) {
      return ''; // silently fail — chart still works without AI
    }
  }

  // ── Feature 2: Pattern Explainer ─────────────────────
  Future<String> explainPattern({
    required String patternName,
    required String symbol,
  }) async {
    try {
      final response = await _dio.post(
        '/ai/pattern-explain',
        data: {'pattern_name': patternName, 'symbol': symbol},
      ).timeout(const Duration(seconds: 6));
      return response.data['explanation'] as String;
    } catch (_) {
      return 'Pattern explanation unavailable.';
    }
  }

  // ── Feature 3: Sentiment Summary ─────────────────────
  Future<SentimentResult> getSentiment({
    required String symbol,
    required String companyName,
    required List<String> headlines,
  }) async {
    try {
      final response = await _dio.post(
        '/ai/sentiment',
        data: {
          'symbol': symbol,
          'company_name': companyName,
          'headlines': headlines,
        },
      ).timeout(const Duration(seconds: 7));
      return SentimentResult.fromJson(response.data);
    } catch (_) {
      return SentimentResult.empty();
    }
  }
}

class SentimentResult {
  final String summary;
  final String sentiment; // positive | negative | neutral | mixed
  final int positiveCount;
  final int negativeCount;
  final int neutralCount;

  const SentimentResult({
    required this.summary,
    required this.sentiment,
    required this.positiveCount,
    required this.negativeCount,
    required this.neutralCount,
  });

  factory SentimentResult.fromJson(Map<String, dynamic> j) =>
      SentimentResult(
        summary: j['summary'] ?? '',
        sentiment: j['sentiment'] ?? 'neutral',
        positiveCount: j['positive_count'] ?? 0,
        negativeCount: j['negative_count'] ?? 0,
        neutralCount: j['neutral_count'] ?? 0,
      );

  factory SentimentResult.empty() => const SentimentResult(
        summary: '',
        sentiment: 'neutral',
        positiveCount: 0,
        negativeCount: 0,
        neutralCount: 0,
      );
}
```

---

## Phase 4 — UI Components

### Chart Insight Line Widget

```dart
// Shown beneath the candlestick chart
// Loads async — chart renders first, AI loads after

class AiInsightLine extends StatelessWidget {
  final Future<String> insightFuture;

  const AiInsightLine({required this.insightFuture});

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<String>(
      future: insightFuture,
      builder: (context, snapshot) {
        // AI loading — show shimmer, chart already visible
        if (snapshot.connectionState == ConnectionState.waiting) {
          return _ShimmerLine();
        }

        final insight = snapshot.data ?? '';
        if (insight.isEmpty) return const SizedBox.shrink();

        return Container(
          margin: const EdgeInsets.fromLTRB(16, 8, 16, 0),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: const Color(0xFF1C2128),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: const Color(0xFF0A7A6E).withOpacity(0.3),
            ),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('🤖 ', style: TextStyle(fontSize: 14)),
              Expanded(
                child: Text(
                  insight,
                  style: const TextStyle(
                    color: Color(0xFFB0B8C4),
                    fontSize: 13,
                    height: 1.4,
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
```

### Sentiment Badge Widget

```dart
// Shown on stock detail screen under company name
class SentimentBadge extends StatelessWidget {
  final SentimentResult result;

  const SentimentBadge({required this.result});

  @override
  Widget build(BuildContext context) {
    if (result.summary.isEmpty) return const SizedBox.shrink();

    final (color, icon) = switch (result.sentiment) {
      'positive' => (const Color(0xFF2ECC71), '📈'),
      'negative' => (const Color(0xFFE74C3C), '📉'),
      'mixed'    => (const Color(0xFFC9A84C), '↔️'),
      _          => (const Color(0xFF8B949E), '➖'),
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(icon, style: const TextStyle(fontSize: 12)),
          const SizedBox(width: 6),
          Text(
            result.summary,
            style: TextStyle(color: color, fontSize: 12),
          ),
        ],
      ),
    );
  }
}
```

### Pattern Explainer Bottom Sheet

```dart
// Called when user taps a detected pattern on chart
Future<void> showPatternExplainer(
  BuildContext context,
  String patternName,
  String symbol,
  AiService aiService,
) async {
  showModalBottomSheet(
    context: context,
    backgroundColor: const Color(0xFF161B22),
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
    ),
    builder: (_) => FutureBuilder<String>(
      future: aiService.explainPattern(
        patternName: patternName,
        symbol: symbol,
      ),
      builder: (context, snapshot) {
        return Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                patternName,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 4),
              const Text(
                'Pattern explanation',
                style: TextStyle(color: Color(0xFF8B949E), fontSize: 13),
              ),
              const SizedBox(height: 16),
              if (snapshot.connectionState == ConnectionState.waiting)
                const CircularProgressIndicator(
                  color: Color(0xFF0A7A6E),
                  strokeWidth: 2,
                )
              else
                Text(
                  snapshot.data ?? 'Explanation unavailable.',
                  style: const TextStyle(
                    color: Color(0xFFB0B8C4),
                    fontSize: 14,
                    height: 1.6,
                  ),
                ),
              const SizedBox(height: 24),
            ],
          ),
        );
      },
    ),
  );
}
```

---

## API Call Budget (Free Tier)

NVIDIA NIM free = **1,000 calls/month**

| Feature | Calls per active user/day | 100 users/day |
|---|---|---|
| Chart Insight | ~3 (open 3 stocks) | 300/day |
| Pattern Explain | ~1 | 100/day |
| Sentiment | ~2 | 200/day |
| **Total** | **~6/user/day** | **600/day = 18,000/month** |

**Free tier runs out at ~50 daily active users.**

When you hit that — upgrade to NVIDIA NIM paid ($0.35/million tokens, Mistral 7B) or switch the same code to **Groq API** (faster, free 14,400 requests/day on Llama 3) by just changing `base_url` and `api_key`. Zero other code changes needed since both are OpenAI-compatible.

---

## Integration Order

```
Week 1  → Backend ai_service.py + routes
Week 2  → Flutter AiService + AiInsightLine widget on chart screen  
Week 3  → SentimentBadge on stock detail screen
Week 4  → Pattern explainer bottom sheet
Week 5  → Test with real stocks, tune prompts, verify sanitizer works
```

---

*Start with Chart Insight — it's the most visible and highest value feature.*
