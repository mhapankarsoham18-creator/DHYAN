# Dhyan — App Structure & Logic
**Version:** 1.0  
**Date:** March 2026

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│                  Flutter App                     │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │   UI     │  │  State   │  │    Services   │  │
│  │  Screens │  │  Riverpod│  │  API Clients  │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
└─────────────────────────┬───────────────────────┘
                          │ HTTPS + WSS
┌─────────────────────────▼───────────────────────┐
│              FastAPI Backend (Python)            │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  Auth    │  │  Broker  │  │  Alert Engine │  │
│  │  Module  │  │Aggregator│  │  (scheduler)  │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  Fee     │  │  Market  │  │  Journal      │  │
│  │  Service │  │  Data    │  │  Service      │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
└──────┬──────────────┬──────────────┬─────────────┘
       │              │              │
┌──────▼───┐  ┌───────▼──┐  ┌───────▼──────────────┐
│ Firebase │  │PostgreSQL│  │   Broker APIs        │
│ Auth +   │  │(Supabase)│  │ Angel One / Upstox   │
│Firestore │  │          │  │ Shoonya / CoinDCX    │
└──────────┘  └──────────┘  └──────────────────────┘
```

---

## 2. Tech Stack — Full Specification

### 2.1 Mobile (Flutter)

| Component | Library | Purpose |
|---|---|---|
| Framework | Flutter 3.x | Cross-platform Android + iOS |
| Language | Dart 3.x | Type-safe, null-safe |
| State Management | Riverpod 2.x | Reactive, testable state |
| Navigation | go_router | Declarative routing, deep links |
| HTTP Client | dio | Interceptors, auth token injection |
| WebSocket | web_socket_channel | Real-time price feeds |
| Charts | fl_chart | Candlestick, line, bar charts |
| Local Storage | flutter_secure_storage | Encrypted token storage |
| Push Notifications | firebase_messaging | FCM for alerts |
| Biometrics | local_auth | Fingerprint / FaceID lock |
| App Lock | flutter_screen_lock | PIN + biometric gate |
| Offline Cache | hive | Fast local key-value store |
| Analytics | firebase_analytics | Crash + usage tracking |
| Crashlytics | firebase_crashlytics | Error reporting |
| Localization | flutter_localizations | English + Hindi |
| Certificate Pinning | dio_certificate_pinner | Network security |

### 2.2 Backend (FastAPI)

| Component | Library | Purpose |
|---|---|---|
| Framework | FastAPI 0.110+ | Async Python API |
| Language | Python 3.11+ | |
| ORM | SQLAlchemy 2.x + Alembic | DB models + migrations |
| Task Queue | APScheduler | Alert engine cron jobs |
| WebSocket | FastAPI WebSocket | Real-time price relay |
| Caching | Redis (Upstash free tier) | Rate limiting, session cache |
| Secrets | python-dotenv + Render env vars | Environment variables |
| Logging | structlog | Structured JSON logs |
| Testing | pytest + httpx | Unit + integration tests |

### 2.3 Infrastructure

| Service | Provider | Tier | Purpose |
|---|---|---|---|
| Backend hosting | Render | Free (spins down on inactivity) → Paid $7/mo at scale | FastAPI server |
| Database | Supabase | Free 500MB PostgreSQL | User data, trades, journals |
| Auth | Firebase Auth | Free | Phone OTP + email auth |
| Push notifications | Firebase FCM | Free | Alert delivery |
| Real-time DB | Firebase Firestore | Free 1GB | Watchlists, settings |
| Cache / Queue | Upstash Redis | Free 10k/day | Rate limiting, sessions |
| APK Builds | GitHub Actions | Free | CI/CD pipeline |
| IPA Builds | Codemagic | Free 500 min/mo | iOS builds |
| App Distribution | Firebase App Distribution | Free | Beta testing |
| Monitoring | Sentry | Free 5k errors/mo | Error tracking |

> **Render free tier caveat:** Server sleeps after 15 minutes inactivity. For market-hours alert engine (needs to be always-on 9:00–15:30 IST), use a free UptimeRobot ping every 10 minutes to keep it awake. At scale (Phase 3+), upgrade to Render Starter ($7/month) or migrate to Oracle Cloud Always Free (free real VPS, best long-term option).

> **Supabase note:** Supabase gives PostgreSQL + built-in REST API + Auth as bonus. Use SQLAlchemy pointing at Supabase PostgreSQL connection string — zero migration effort from Railway PostgreSQL.

### 2.4 Broker APIs

| Broker | API | Cost | Order Placement | Market Data |
|---|---|---|---|---|
| Angel One | SmartAPI | **Free** | Yes — OAuth 2.0 | Yes — included |
| Upstox | API v2 | **Free** | Yes — OAuth 2.0 | Yes — included |
| Finvasia Shoonya | Shoonya API | **Free** | Yes — zero brokerage too | Yes — included |
| Fyers | Fyers API v3 | **Free** (approval needed) | Yes — OAuth 2.0 | Yes — included |
| Zerodha | Personal API | **Free** | Yes — OAuth 2.0 | ❌ Paid separately |
| Crypto | CoinDCX API | **Free** | Yes — API Key | Yes — included |

> **Broker priority for v1:** Angel One (primary — best free API + data) → Upstox (secondary) → Shoonya (tertiary, zero brokerage bonus). Add Zerodha Personal API only when users specifically request it — skip the paid Kite Connect entirely.

> **Market data for Zerodha users:** If a Zerodha user connects, use Angel One's free WebSocket for live prices (same NSE data, same feed). Order execution goes through Zerodha Personal API. Data and execution can be from different providers — the broker abstraction layer handles this cleanly.

---

## 3. App Screen Structure

```
Dhyan App
├── Onboarding Flow
│   ├── Splash Screen
│   ├── Welcome Screen
│   ├── Profile Quiz (5 questions)
│   └── Paper Trading Introduction
│
├── Auth Flow
│   ├── Phone Number Entry
│   ├── OTP Verification
│   └── PIN Setup
│
├── Main App (Bottom Nav)
│   ├── Home (Dashboard)
│   ├── Markets
│   ├── Trade
│   ├── Alerts
│   └── Profile
│
├── Home Tab
│   ├── Portfolio Summary Card
│   ├── Today's P&L
│   ├── Positions Needing Attention
│   ├── Active Alerts (3 max visible)
│   └── Weekly Report Card (Sundays)
│
├── Markets Tab
│   ├── Watchlist (default)
│   ├── Search
│   ├── Stock Detail Screen
│   │   ├── Chart (candlestick default)
│   │   ├── AI Insight Line
│   │   ├── Key Stats
│   │   ├── Order Button
│   │   └── Jargon Tooltip System
│   └── Sector Heatmap
│
├── Trade Tab
│   ├── Quick Order Templates
│   ├── Order Book (open orders)
│   ├── Order History
│   └── Pre-Trade Context Card (overlay)
│
├── Alerts Tab
│   ├── Active Alerts List
│   ├── Create Alert
│   │   ├── Simple (price target)
│   │   └── Advanced (condition builder)
│   ├── Alert History
│   └── Focus Mode Toggle
│
├── Profile Tab
│   ├── Connected Brokers
│   ├── Broker Connect Flow (OAuth)
│   ├── Fee Summary
│   ├── Trading Journal
│   ├── Weekly Reports Archive
│   ├── Settings
│   │   ├── Simple Mode / Finance Mode
│   │   ├── Daily Trade Budget
│   │   ├── Notification Preferences
│   │   ├── Biometric Lock
│   │   └── Privacy & Security
│   └── Paper Trading Mode Toggle
│
└── Overlay Screens
    ├── Order Placement Sheet (bottom)
    ├── Pre-Trade Context Card
    ├── Post-Trade Summary Card
    ├── Revenge Trade Warning
    ├── Jargon Tooltip Sheet
    └── All-In Cost Breakdown
```

---

## 4. Core Logic Flows

### 4.1 Onboarding & First Session

```
App Launch
    │
    ▼
First time? ──YES──► Splash → Welcome → Profile Quiz
    │                              │
    NO                             ▼
    │                    Quiz Results Processed
    ▼                              │
Auth Check                No commerce bg? ──YES──► Simple Mode ON
    │                              │                F&O Hidden
    │                              NO
    │                              ▼
    │                    Full Mode Available
    │                              │
    ▼                              ▼
PIN / Biometric             Paper Trading Intro
    │                              │
    ▼                              ▼
Main App                    ₹1L Virtual Balance
                            7-Day Challenge Starts
```

### 4.2 Broker OAuth Connect Flow

```
User taps "Connect Broker"
    │
    ▼
Select broker (Angel One / Upstox / Zerodha)
    │
    ▼
App generates OAuth URL with state parameter (CSRF protection)
    │
    ▼
Opens broker's login page in secure in-app browser
    │
    ▼
User logs in on BROKER'S OWN PAGE (app never sees credentials)
    │
    ▼
Broker redirects to Dhyan deep link with auth code
    │
    ▼
Backend exchanges auth code for access_token + refresh_token
    │
    ▼
Tokens stored: access_token in Redis (short TTL)
               refresh_token in PostgreSQL (AES-256 encrypted)
    │
    ▼
Portfolio data fetched and cached in Firestore
    │
    ▼
Dashboard updates with real broker data
```

### 4.3 Order Placement Flow

```
User initiates order (from chart / template / notification)
    │
    ▼
Order sheet opens (bottom sheet)
    │
    ▼
Real-time all-in cost calculated and displayed
Broker fee + STT + GST + Exchange + Dhyan fee (if applicable)
    │
    ▼
PRE-TRADE CONTEXT CARD (3 seconds, skippable)
Shows: Today's P&L | This week's win rate | Trade reason
    │
    ▼
User confirms (swipe-up gesture or tap confirm)
    │
    ▼
Dhyan backend receives order request
    │
    ▼
Fee check: Delivery? → ₹0 Dhyan fee
           Intraday/F&O? → First 10 free this month?
                           YES → ₹0
                           NO → ₹5 logged
    │
    ▼
Order forwarded to broker API via authenticated session
    │
    ▼
Broker executes order (all compliance on broker side)
    │
    ▼
Order confirmation received
    │
    ▼
POST-TRADE PLAIN LANGUAGE CARD shown (30 seconds)
"You bought X shares of Y at ₹Z..."
    │
    ▼
Portfolio cache invalidated → fresh data fetched
    │
    ▼
Trade logged to PostgreSQL with timestamp, reason, emotion
```

### 4.4 Alert Engine Flow

```
User creates alert (e.g. "Alert me when Infosys > ₹1800")
    │
    ▼
Alert stored in PostgreSQL
    │
    ▼
APScheduler job runs every 30 seconds during market hours
    │
    ▼
Fetches latest prices from broker WebSocket / Angel One feed
    │
    ▼
Evaluates all active alerts against current prices
    │
    ▼
Condition met? ──NO──► Continue polling
    │
    YES
    ▼
FCM push notification sent with action button
    │
    ▼
User receives: "Infosys hit ₹1,800 [Buy Now] [Dismiss]"
    │
    ▼
"Buy Now" tapped → deep link opens order sheet pre-filled
    │
    ▼
Alert marked triggered, user can reset or delete
```

### 4.5 Revenge Trade Detection

```
Trade executed
    │
    ▼
Was it a loss? (closing price < entry price)
    │
    YES
    ▼
Start 10-minute watch window
    │
    ▼
User places another trade within window?
    │
    YES
    ▼
Counter increments (1, 2, 3...)
    │
    ▼
Counter hits 3?
    │
    YES
    ▼
Non-blocking card shown:
"You've made 3 trades quickly after a loss. Take a breath?"
[Keep Trading] [Pause for now]
    │
    ▼
Choice logged to journal anonymously
    │
    ▼
Weekly report includes: "You paused trading 2x after losses this week"
```

---

## 5. Data Models

### 5.1 User
```python
class User:
    id: UUID
    phone: str (hashed)
    email: Optional[str]
    profile_quiz_result: JSON  # risk_tolerance, goal, horizon, bg
    mode: Enum["simple", "finance"]
    daily_trade_budget: Optional[int]
    created_at: datetime
    is_paper_mode: bool
    paper_balance: Decimal  # default 100000
    subscription_tier: Enum["free", "premium"]
    subscription_expires: Optional[datetime]
```

### 5.2 BrokerConnection
```python
class BrokerConnection:
    id: UUID
    user_id: UUID
    broker: Enum["angel_one", "upstox", "coindcx"]
    access_token: str  # AES-256 encrypted
    refresh_token: str  # AES-256 encrypted
    token_expiry: datetime
    is_active: bool
    connected_at: datetime
```

### 5.3 Order
```python
class Order:
    id: UUID
    user_id: UUID
    broker: str
    symbol: str
    exchange: Enum["NSE", "BSE", "NFO", "CDS", "CRYPTO"]
    order_type: Enum["market", "limit", "sl", "sl-m"]
    product_type: Enum["CNC", "MIS", "NRML"]
    side: Enum["buy", "sell"]
    quantity: int
    price: Optional[Decimal]
    trigger_price: Optional[Decimal]
    status: Enum["pending", "executed", "cancelled", "rejected"]
    dhyan_fee: Decimal  # 0 or 5
    broker_order_id: str
    executed_at: Optional[datetime]
    user_reason: Optional[str]  # why they traded
    emotion_before: Optional[Enum["calm", "anxious", "excited"]]
```

### 5.4 Alert
```python
class Alert:
    id: UUID
    user_id: UUID
    symbol: str
    condition: Enum["above", "below", "pct_change", "drawdown", "volume_spike"]
    target_value: Decimal
    is_active: bool
    created_at: datetime
    triggered_at: Optional[datetime]
    action_template_id: Optional[UUID]  # for one-tap order
```

### 5.5 JournalEntry
```python
class JournalEntry:
    id: UUID
    user_id: UUID
    date: date
    emotion: Enum["neutral", "anxious", "confident"]
    note: Optional[str]
    trades_count: int
    day_pnl: Decimal
    revenge_interventions: int
    created_at: datetime
```

---

## 6. State Management (Riverpod)

```dart
// Core providers
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>
final portfolioProvider = FutureProvider<Portfolio>
final watchlistProvider = StateNotifierProvider<WatchlistNotifier, List<Stock>>
final alertsProvider = StateNotifierProvider<AlertsNotifier, List<Alert>>
final priceStreamProvider = StreamProvider.family<Price, String>  // per symbol
final paperTradingProvider = StateNotifierProvider<PaperTradingNotifier, PaperPortfolio>
final userPrefsProvider = StateNotifierProvider<UserPrefsNotifier, UserPrefs>
final orderSheetProvider = StateNotifierProvider<OrderSheetNotifier, OrderSheetState>
```

---

## 7. API Abstraction Layer

All broker integrations behind a single interface so swapping a broker doesn't break the app:

```python
class BrokerInterface(ABC):
    async def get_portfolio(self) -> Portfolio
    async def get_positions(self) -> List[Position]
    async def get_holdings(self) -> List[Holding]
    async def place_order(self, order: OrderRequest) -> OrderResponse
    async def cancel_order(self, order_id: str) -> bool
    async def get_order_history(self) -> List[Order]
    async def get_quote(self, symbol: str) -> Quote
    async def subscribe_price_feed(self, symbols: List[str]) -> AsyncGenerator

class AngelOneClient(BrokerInterface): ...
class UpstoxClient(BrokerInterface): ...
class ZerodhaClient(BrokerInterface): ...
class CoinDCXClient(BrokerInterface): ...
class PaperTradingClient(BrokerInterface): ...  # same interface, fake execution
```

This pattern means paper trading and real trading use identical code paths — only the client swaps.

---

## 8. Fee Calculation Engine

```python
def calculate_fees(order: OrderRequest, user: User) -> FeeBreakdown:
    dhyan_fee = 0.0

    if order.product_type == "CNC":  # delivery
        dhyan_fee = 0.0
    else:  # intraday or F&O
        trades_this_month = get_monthly_trade_count(user.id)
        if trades_this_month >= 10:  # free tier exhausted
            dhyan_fee = 5.0

    # Statutory charges (cannot be zero, government mandated)
    stt = calculate_stt(order)
    gst = calculate_gst(order)
    exchange_charges = calculate_exchange_charges(order)
    sebi_charges = calculate_sebi_charges(order)
    stamp_duty = calculate_stamp_duty(order)

    return FeeBreakdown(
        broker_fee=0.0 if order.product_type == "CNC" else 20.0,
        stt=stt,
        gst=gst,
        exchange_charges=exchange_charges,
        sebi_charges=sebi_charges,
        stamp_duty=stamp_duty,
        dhyan_fee=dhyan_fee,
        total=sum(all above)
    )
```

---

## 9. Real-Time Architecture

```
Broker WebSocket (price feed)
    │
    ▼
Backend WebSocket relay
(normalises format across all brokers)
    │
    ▼
Redis pub/sub channel per symbol
    │
    ▼
Flutter app subscribes via WebSocket
    │
    ▼
Riverpod StreamProvider updates UI reactively
(only re-renders price display widget, not entire screen)
```

Price feed hierarchy:
1. Angel One WebSocket (free, primary for stocks)
2. Upstox WebSocket (free, backup)
3. Yahoo Finance API (fallback for non-trading hours)

---

*Document Owner: CSIT Mumbai University Charity Initiative*
