# Dhyan — Phase-wise Development Plan
**Pre-Production → Production → APK/IPA Deployment**  
**Version:** 1.0 | **Date:** March 2026

---

## Overview Timeline

```
Month 0      Month 1-2       Month 3-4       Month 5-6       Month 7-8
    │              │               │               │               │
    ▼              ▼               ▼               ▼               ▼
[Pre-Prod]    [Phase 1]       [Phase 2]       [Phase 3]       [Phase 4]
Planning      Foundation      Core Features   Real Trading    Scale &
& Setup       + Paper Trade   + Alerts        + Monetise      Premium
```

---

## Phase 0 — Pre-Production (Week 1-3)

Status: Completed — March 2026

### 0.1 Legal & Compliance Setup
- [x] College files for legal entity (Section 8 non-profit company OR LLP)
- [x] Open entity bank account (required for ₹5 fee collection later)
- [x] Review broker API Terms of Service (Angel One, Upstox, Zerodha)
- [x] Confirm third-party fee collection permitted in API agreements
- [x] Draft privacy policy and terms of service (DPDP Act 2023 compliant)
- [x] SEBI disclosure language for all fee screens reviewed by advisor

### 0.2 Design System Setup
- [x] Finalise brand identity: Dhyan logo, dark mode colour palette
  - Primary: Deep teal (#0A7A6E)
  - Background: Near-black (#0D1117)
  - Accent: Soft gold (#C9A84C)
  - Success: Muted green (#2ECC71)
  - Danger: Muted red (#E74C3C)
- [x] Create Figma design system (typography, components, spacing)
- [x] Design all 30 core screens in Figma (mobile, dark mode first)
- [x] Accessibility review: colour contrast, touch target sizes (min 44×44px)

### 0.3 Development Environment
- [x] Flutter 3.x + Dart 3.x setup
- [x] Python 3.11 + FastAPI setup
- [x] Git repository (GitHub, private)
- [x] GitHub Actions CI/CD pipeline configured
- [x] Codemagic account set up (iOS builds)
- [x] Firebase project created (Auth, Firestore, FCM, Crashlytics)
- [x] Railway project created (FastAPI + PostgreSQL)
- [x] Upstash Redis configured
- [x] Sentry project created

### 0.4 Broker API Registration
- [x] Angel One SmartAPI — register developer account, get API key (free, priority first)
- [x] Upstox API v2 — register developer account, get OAuth credentials (free)
- [x] Finvasia Shoonya — register developer account (free, zero brokerage bonus)
- [x] Fyers API v3 — apply for API access (free, needs approval, allow 2-3 days)
- [x] Zerodha Personal API — register (free, skip paid Kite Connect entirely)
- [x] CoinDCX — register developer account (free, for crypto)
- [x] Test OAuth flows in sandbox/paper environments for each broker
- [x] UptimeRobot — set up free ping to keep Render server awake during market hours

### 0.5 Architecture Scaffolding
- [x] Flutter project structure created (feature-first architecture)
- [x] FastAPI project structure created
- [x] PostgreSQL schema designed and Alembic migrations written
- [x] Broker abstraction interface defined
- [x] Environment variable management configured (no secrets in git)

**Exit criteria:** Design done, dev env ready, all API credentials obtained, legal entity initiated.  
Status: Completed — All exit criteria met.

---

## Phase 1 — Foundation (Month 1-2)

**Goal:** Working app with paper trading, auth, portfolio view. Real users can onboard and learn without real money.

Status: Completed — Month 2

### 1.1 Authentication (Week 1-2)
- [x] Phone OTP login via Firebase Auth
- [x] OTP screen UI
- [x] PIN setup screen (4-6 digit PIN)
- [x] Biometric lock (fingerprint / FaceID) via `local_auth`
- [x] JWT session management on backend
- [x] Auto-logout after 30 minutes inactivity
- [x] Device binding (each account limited to 2 devices)

**Test:** Full auth flow works on Android emulator and iOS simulator — PASSED.

### 1.2 Onboarding Flow (Week 2)
- [x] Splash screen (Dhyan logo, 2 second max)
- [x] Welcome screen
- [x] Profile quiz (5 questions, animated transitions)
- [x] Quiz result processing → user preferences saved
- [x] Simple Mode default for non-commerce users
- [x] Paper trading intro screen
- [x] ₹1,00,000 virtual balance created on account creation

**Test:** New user can complete onboarding in under 3 minutes without confusion — PASSED.

### 1.3 Paper Trading Engine (Week 3-4)
- [x] Paper trading client implementing BrokerInterface
- [x] Virtual order placement (market and limit orders)
- [x] Virtual portfolio calculation (unrealised P&L)
- [x] Real market prices via Angel One free feed
- [x] 7-day challenge tracking (start date, daily P&L progression)
- [x] Paper trading leaderboard (college-internal, optional)
- [x] "Switch to real trading" nudge after 7 days

**Test:** Paper trades execute correctly, P&L calculates accurately against real prices — PASSED.

### 1.4 Home Dashboard (Week 3-4)
- [x] Portfolio summary card (total value, day P&L, total P&L)
- [x] Paper mode badge (clearly visible when in paper mode)
- [x] Positions list (symbol, qty, avg price, LTP, P&L)
- [x] Stale-while-revalidate pattern (cached data loads instantly)
- [x] Pull-to-refresh
- [x] Empty state (first-time user, no positions yet)

**Test:** Dashboard loads in under 2 seconds on mid-range Android device (4GB RAM) — PASSED.

### 1.5 Markets & Search (Week 5-6)
- [x] Watchlist screen (default + custom lists)
- [x] Stock search (NSE/BSE symbols + company names)
- [x] Stock detail screen (basic info, price, change)
- [x] Candlestick chart via `fl_chart` (1D, 1W, 1M, 3M, 1Y)
- [x] Volume bars beneath chart
- [x] Key stats: 52-week high/low, P/E, market cap
- [x] Jargon tooltip system (every term tappable)
- [x] Add/remove from watchlist

**Test:** Jargon tooltip works for all 25 defined financial terms. Charts render correctly — PASSED.

### 1.6 Basic Order Flow — Paper Only (Week 6-8)
- [x] Order bottom sheet (slides up from chart screen)
- [x] Market and limit order types
- [x] CNC / MIS product type selector
- [x] Quantity input with value preview (qty × price = ₹X)
- [x] Paper fee display: ₹0 for all paper trades
- [x] Order confirmation with swipe gesture
- [x] Post-trade plain language card
- [x] Order history screen

**Test:** Complete paper trade in under 5 taps. Post-trade card displays correctly — PASSED.

### 1.7 CI/CD Pipeline (Week 1, maintained throughout)
- [x] GitHub Actions: on push to `main` → run tests → build APK
- [x] Codemagic: on push to `main` → build IPA (unsigned for testing)
- [x] Firebase App Distribution: auto-distribute APK to beta testers
- [x] Test flight: internal testing track for IPA
- [x] Automated Flutter tests: unit + widget tests (target 70% coverage)

**Exit criteria:** All section-level tests passed; CI/CD pipelines green; APK and IPA artifacts built; ≥70% automated test coverage achieved; APK distributed via Firebase App Distribution and IPA via TestFlight (internal) to 50 beta testers.

**Phase 1 Deliverable:** Working Flutter app with paper trading, deployable as APK (Android) and IPA (iOS internal). Distribute to 50 beta testers (college students). — DELIVERED.

---

## Phase 2 — Core Features (Month 3-4)

**Goal:** Smart alert engine, behavioural layer, full charts, Focus Mode. App is genuinely useful even without real broker connection.

Status: Completed — Month 4

### 2.1 Alert Engine (Week 9-11)
- [x] Alert creation screen (simple: price target)
- [x] Alert condition builder (advanced: %, drawdown, volume)
- [x] APScheduler backend job (polls prices every 30 seconds, market hours only)
- [x] FCM push notification delivery
- [x] Actionable notification with inline order button
- [x] Deep link from notification → pre-filled order sheet
- [x] Alert history (triggered, dismissed, expired)
- [x] Alert limit: 10 free, unlimited for premium (Phase 3)

**Test:** Alert triggers within 60 seconds of condition being met. Notification deep link works correctly. — PASSED.

### 2.2 Focus Mode (Week 10)
- [x] Focus Mode toggle on Alerts tab
- [x] When active: suppress all unsolicited price notifications
- [x] Daily condition configuration: "Only alert me if Nifty moves >1%"
- [x] Active Focus Mode badge on home screen
- [x] Auto-disable at 3:30 PM (market close)

### 2.3 Behavioural Layer (Week 11-13)
- [x] Pre-trade context card (3-second overlay before confirmation)
- [x] Revenge trade detector (tracks loss → rapid trade pattern)
- [x] Revenge trade warning card (non-blocking)
- [x] Daily trade budget setting and warning
- [x] End-of-day journal prompt (3:45 PM push, optional)
- [x] Journal entry screen (emotion picker + text field)
- [x] All interactions and choices logged to PostgreSQL

### 2.4 Advanced Charts (Week 12-13)
- [x] Indicator layer: RSI, MACD, Bollinger Bands, EMA(20), EMA(50), VWAP
- [x] Indicators hidden by default, accessible via "+" button
- [x] AI insight line beneath chart (rule-based, not ML in v1):
  - RSI < 30: "RSI oversold — last 3 times this happened stock rose avg 3.2%"
  - RSI > 70: "RSI overbought — consider setting a target or stop-loss"
  - Price near 52w low: "Near 52-week low — historically strong support zone"
- [x] Fullscreen chart mode
- [x] Compare two stocks on same chart

### 2.5 Weekly Trading Report (Week 13-14)
- [x] Backend job generates weekly summary every Sunday 7 PM IST
- [x] Plain language narrative generation (template-based)
- [x] FCM delivery
- [x] In-app weekly report screen (archive of all past reports)
- [x] Stats: trades count, win rate, best trade, worst trade, total P&L

### 2.6 Confidence Indicators + Simple/Finance Mode (Week 14)
- [x] Simple Mode UI pass: replace all jargon strings with plain equivalents
- [x] Finance Mode UI: restore original terminology
- [x] Per-screen toggle stored in user preferences
- [x] Confidence indicator dots implemented on all action buttons
- [x] "Post-trade plain language card" fully implemented for all order types

**Exit criteria:** Alert engine triggers within 60 seconds and deep links open pre-filled order sheet; Focus Mode suppresses unsolicited notifications and auto-disables at 3:30 PM; behavioural features active and all interactions logged to PostgreSQL; advanced chart indicators and AI insight line available and hidden by default; weekly report job delivers via FCM with in-app archive; Simple/Finance Mode toggle persists; confidence indicators present; post-trade plain language card implemented for all order types; public beta builds available on Play Store (internal testing track) and TestFlight.

**Phase 2 Deliverable:** Full-featured app. Deploy as public beta on Play Store (internal testing track) and TestFlight. Target 500 beta users. — DELIVERED.

---

## Phase 3 — Real Trading Integration (Month 5-6)

**Goal:** Connect real broker accounts, live order placement, fee collection, full multi-broker portfolio.

Status: Completed — Month 6

### 3.1 Broker OAuth Implementation (Week 15-17)
- [x] Angel One OAuth 2.0 flow (primary — free API)
- [x] Upstox OAuth 2.0 flow (secondary — free API)
- [x] Zerodha Kite Connect OAuth (tertiary — ₹500/month)
- [x] CoinDCX API key connection
- [x] Secure token storage: AES-256 encrypted in PostgreSQL
- [x] Token refresh logic (auto-renew before expiry)
- [x] Multi-broker aggregation: unified portfolio from all connected accounts
- [x] Disconnect broker flow (clears tokens securely)

### 3.2 Live Order Placement (Week 16-18)
- [x] Real order routing via broker API (same UI as paper trading)
- [x] Live fee calculation engine (all statutory charges + Dhyan fee)
- [x] Monthly trade counter (for free 10-trade tier)
- [x] Order status polling (pending → executed → settled)
- [x] Order cancellation
- [x] Real position and holding sync post-execution

### 3.3 Fee Infrastructure (Week 17-18)
- [x] Dhyan fee ledger in PostgreSQL (₹5 per qualifying trade)
- [x] Monthly fee statement for users
- [x] Fee collection mechanism (Razorpay integration for collecting ₹5 per trade)
- [x] GST on platform fee (18% — mandatory if entity is registered)
- [x] Transparent fee disclosure on every order ticket (SEBI compliance)

### 3.4 Real-Time Price Feed (Week 17-19)
- [x] Angel One WebSocket integration (live prices during market hours)
- [x] Upstox WebSocket as fallback
- [x] Backend WebSocket relay (normalised format)
- [x] Flutter StreamProvider subscriptions
- [x] Selective subscription (only symbols in watchlist + positions)
- [x] Auto-disconnect outside market hours (save battery)

### 3.5 Production Hardening (Week 19-20)
- [x] Load testing (simulate 10,000 concurrent users)
- [x] Rate limiting on all API endpoints (Redis-based)
- [x] Database query optimisation + indexes
- [x] Error handling for broker API downtime (graceful degradation)
- [x] Broker maintenance window handling (NSE closes Sat/Sun)
- [x] Circuit breaker pattern for broker API calls

**Exit criteria:** Broker OAuth flows verified for all supported brokers; tokens stored with AES-256 encryption and refresh logic active; order placement, status polling, cancellation, and post-execution sync working against real broker APIs; fee engine accurate with statutory charges + Dhyan fee and monthly free-tier counter; fee ledger and user statements generated; transparent fee disclosure on every order ticket; real-time price feed via Angel One with Upstox fallback and backend relay; selective subscriptions and auto-disconnect outside market hours; load tests pass for 10,000 concurrent users; Redis rate limiting enabled; DB indexes and optimisations applied; circuit breaker and graceful degradation for broker downtime; compliance with SEBI disclosure maintained.

**Phase 3 Deliverable:** Production-ready app with real trading. Deploy to Play Store (open testing) and App Store (TestFlight external). Target 5,000 users. — DELIVERED.

---

## Phase 4 — Scale & Premium (Month 7-8)

**Goal:** Premium subscription, Hindi language support, performance optimisation, full public launch.

Status: Completed — Month 8

### 4.1 Premium Subscription (Week 21-23)
- [x] ₹99/month subscription via Razorpay Subscriptions
- [x] Premium features gate: advanced alerts (unlimited), AI insights, tax report, leaderboard
- [x] Free tier clearly defined and permanently maintained
- [x] Subscription management screen (upgrade, downgrade, cancel)
- [x] In-app purchase for iOS (Apple requires it for digital subscriptions)
- [x] Google Play Billing for Android

### 4.2 Hindi Language Support (Week 22-24)
- [x] Flutter localisation for Hindi strings
- [x] Simple Mode in Hindi (jargon replaced by Hindi plain language)
- [x] Language toggle in settings (English / Hindi)
- [x] All push notifications in user's preferred language

### 4.3 Tax P&L Report (Week 23-24)
- [x] Annual P&L calculation (STCG, LTCG, speculative income)
- [x] Downloadable PDF report (CA-friendly format)
- [x] Premium feature

### 4.4 Performance & Polish (Week 24-26)
- [x] App size optimisation (target < 25MB APK, < 50MB IPA)
- [x] Memory profiling and leak fixes
- [x] 60fps animations across all screens
- [x] Offline mode: full portfolio viewable without internet
- [x] Dark mode polishing pass (OLED-optimised blacks)
- [x] Accessibility audit: screen reader support, font scaling

### 4.5 Full Public Launch (Week 26-28)
- [x] Play Store listing: screenshots, description, keywords
- [x] App Store listing: screenshots, description, keywords (Apple review ~7 days)
- [x] Landing page (simple, mobile-first)
- [x] College PR and media outreach
- [x] Social media launch (LinkedIn, Twitter)

**Exit criteria:** Premium subscription live (Razorpay Subscriptions), Google Play Billing and iOS In‑App Purchase enabled; premium gating for advanced alerts, AI insights, tax report, leaderboard active with free tier clearly defined; subscription management supports upgrade/downgrade/cancel; Hindi localisation complete including Simple Mode and push notifications in preferred language; tax P&L report available as downloadable CA‑friendly PDF; performance targets met (<25MB APK, <50MB IPA), memory profiling clean, 60fps animations, offline portfolio view, dark mode polished, accessibility audit completed; Play Store and App Store listings live; landing page published; PR and social launches executed.

**Phase 4 Deliverable:** Full public launch on Play Store and App Store with premium features and Hindi support. — DELIVERED.
---

## Deployment — APK & IPA

### Android APK (Play Store)

```
Development build:
flutter build apk --debug

Staging build:
flutter build apk --release --dart-define=ENV=staging

Production build:
flutter build apk --release --dart-define=ENV=production
flutter build appbundle  # AAB preferred for Play Store

Signing:
keytool -genkey -v -keystore dhyan-release.jks -alias dhyan
flutter build apk --release --keystore=dhyan-release.jks

Distribution:
1. Internal testing → Firebase App Distribution (Phase 1)
2. Closed testing → Play Console (Phase 2-3)
3. Open testing → Play Console (Phase 3)
4. Production release → Play Console (Phase 4)
```

### iOS IPA (App Store)

```
Requires:
- Apple Developer Account (₹8,500/year or $99/year)
- Xcode on macOS (or Codemagic CI)
- Provisioning profiles and certificates

Development build (Codemagic):
flutter build ios --debug --no-codesign

Production build:
flutter build ipa --release
  (triggers Codemagic → signs with distribution certificate)

Distribution:
1. Internal testing → TestFlight (Phase 1)
2. External testing → TestFlight (up to 10,000 testers, Phase 2-3)
3. App Store review submission (Phase 4, allow 7 days)
4. App Store production (Phase 4)

Note: Apple requires In-App Purchase for ₹99/month subscription
(30% Apple cut on subscriptions in year 1, 15% after year 1)
```

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/build.yml
on:
  push:
    branches: [main, staging]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - flutter test
      - flutter analyze

  build-android:
    runs-on: ubuntu-latest
    steps:
      - flutter build apk --release
      - upload to Firebase App Distribution

  build-ios:
    runs-on: [Codemagic]
    steps:
      - flutter build ipa --release
      - upload to TestFlight
```

---

## Environment Management

```
environments/
├── .env.development    (local dev, sandbox broker APIs)
├── .env.staging        (Railway staging, real APIs in test mode)
└── .env.production     (Railway production, live APIs)

Variables:
ANGEL_ONE_API_KEY=...
ANGEL_ONE_CLIENT_ID=...
UPSTOX_CLIENT_ID=...
UPSTOX_CLIENT_SECRET=...
SHOONYA_API_KEY=...
SHOONYA_CLIENT_ID=...
ZERODHA_PERSONAL_API_KEY=...       # free personal API
ZERODHA_PERSONAL_API_SECRET=...
FYERS_CLIENT_ID=...
FYERS_SECRET_KEY=...
COINDCX_API_KEY=...
FIREBASE_PROJECT_ID=...
RAZORPAY_KEY_ID=...
RAZORPAY_KEY_SECRET=...
JWT_SECRET=...
AES_ENCRYPTION_KEY=...
DATABASE_URL=...                   # Supabase PostgreSQL connection string
REDIS_URL=...                      # Upstash Redis URL
SENTRY_DSN=...
```

**Rule:** No secret ever touches the git repository. Environment variables injected at build time via Railway + GitHub Actions secrets.

---

## Budget Summary

| Item | Cost |
|---|---|
| Apple Developer Account | ₹8,500/year |
| Zerodha Personal API | **₹0** (free — no market data, use Angel One feed) |
| Render backend hosting | **₹0** (free tier with UptimeRobot ping) → $7/mo at Phase 3+ |
| Supabase PostgreSQL | **₹0** (free 500MB, upgrades at scale) |
| Domain (dhyan.app or similar) | ₹1,500/year |
| Codemagic (iOS builds) | Free 500 min/month |
| All other infrastructure | Free tier |
| **Total Year 1** | **~₹10,000** (just Apple account + domain) |
| **vs original estimate** | ~~₹22,500~~ → **₹10,000 saved ₹12,500/year** |

**Monthly burn rate at launch: ₹0** (everything on free tiers)  
**Monthly burn at scale (10,000+ users):** ~$7/month Render + Supabase Pro if DB exceeds 500MB

---

*Document Owner: CSIT Mumbai University Charity Initiative*
