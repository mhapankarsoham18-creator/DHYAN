# Dhyan — Product Requirements Document (PRD)
**Version:** 1.0  
**Date:** March 2026  
**Status:** Pre-Production  
**Owner:** CSIT Mumbai University (Charity Initiative)

---

## 1. Product Vision

**Dhyan** (Sanskrit/Hindi: mindfulness, focus) is a broker-agnostic, multi-asset smart trading companion for Android and iOS. It is built as a charitable initiative — free for long-term investors, ₹5/trade for intraday and F&O, with no hidden fees and no predatory engagement mechanics.

**Mission:** Make confident, calm, informed trading accessible to every Indian — regardless of financial background, education, or experience.

**North Star Principle:** Every feature must pass one test — *does this reduce unnecessary screen time, or increase it?* Features that increase screen time without clear user benefit are cut.

---

## 2. The Problem

| Problem | Scale |
|---|---|
| 91% of F&O retail traders lose money | ₹1.06 lakh crore lost in FY2025 |
| Only 24% financial literacy rate in India | 3 in 4 users don't understand what they're doing |
| Every app maximises engagement, not outcomes | Dopamine loops, FOMO-driven trades |
| Jargon walls block non-commerce users | Arts, science, engineering students shut out |
| Hidden fees discovered post-trade | STT, GST surprises after confirmation |
| No unified multi-broker view on mobile | Users juggle 3 apps for stocks, F&O, crypto |

---

## 3. Target Users

### Persona 1 — The Anxious Beginner
- Age: 18-24, college student (any stream)
- Background: No commerce education
- Pain: Afraid of looking stupid, scared of losing money accidentally
- Goal: Learn to invest without a 6-hour course
- Behaviour: Will quit if confused in first 3 minutes

### Persona 2 — The Emotional Active Trader
- Age: 25-35, working professional
- Background: Knows the basics, has a broker account
- Pain: Revenge trades, FOMO, too much screen time
- Goal: Trade with discipline, stop emotional decisions
- Behaviour: Checks markets 15+ times a day

### Persona 3 — The Disciplined Long-Term Investor
- Age: 28-45, salaried employee
- Background: SIPs, some stocks, basic knowledge
- Pain: Scattered across Zerodha, Groww, CoinDCX
- Goal: Single unified view, minimal maintenance
- Behaviour: Checks portfolio weekly, not daily

### Persona 4 — The Informed Student
- Age: 20-26, commerce/finance student or self-taught
- Background: Understands markets, wants professional tools
- Pain: Existing apps either too simple (Groww) or too complex (Kite)
- Goal: Powerful features without clutter
- Behaviour: Power user who values speed and efficiency

---

## 4. Core Feature Set

### 4.1 Onboarding
**FR-001 — Profile Quiz**
- 5-question onboarding quiz (risk tolerance, goal, time horizon, trading frequency, background)
- App personalises entire experience based on responses
- No commerce background → Simple Mode default, F&O hidden
- Commerce background → Full Mode available

**FR-002 — Paper Trading Default**
- All new users start in Paper Mode with ₹1,00,000 virtual money
- Real market prices, zero real money
- 7-day challenge framing: "See how you'd do"
- After 7 days: natural nudge to connect broker (not forced)

**FR-003 — KYC-Free Start**
- Zero KYC required to use Paper Mode and read-only portfolio features
- KYC (via broker OAuth) only required to place real trades
- Friction added deliberately at real-money threshold

---

### 4.2 Multi-Broker Integration
**FR-004 — Broker OAuth Connect**
- Supported brokers: Angel One (SmartAPI), Upstox (API v2), Zerodha (Kite Connect)
- Standard OAuth 2.0 flow — user logs in on broker's own page
- App never sees broker password
- Support for multiple broker accounts simultaneously

**FR-005 — Unified Portfolio Dashboard**
- All connected broker accounts aggregated in one view
- Stocks + F&O + crypto (CoinDCX) in single dashboard
- Total P&L, day's P&L, allocation breakdown
- Positions that need attention surfaced at top

**FR-006 — Crypto Integration**
- CoinDCX API for crypto portfolio and trading
- Same OAuth connect flow
- BTC, ETH, top 20 Indian-traded crypto pairs

---

### 4.3 Smart Alert Engine
**FR-007 — Condition-Based Alerts**
- Price target alerts (above/below)
- Percentage change alerts
- Portfolio drawdown alerts
- Volume spike alerts
- Custom condition builder for advanced users

**FR-008 — Actionable Notifications**
- Every alert has inline action button
- User can place order directly from notification without opening app
- "Buy 5 Infosys at market" confirmable in one tap from lock screen

**FR-009 — Focus Mode**
- User sets conditions for the day
- App goes completely silent outside those conditions
- No price tickers, no unsolicited notifications
- Inverse of every competitor's engagement model

---

### 4.4 Order Flow
**FR-010 — Quick Order Templates**
- Pre-saved order configurations (e.g. "Buy 10 Reliance, CNC, market")
- Execute in 2 taps from anywhere in the app
- Template library manageable from settings

**FR-011 — Pre-Trade Context Card**
- Shown before every order confirmation
- Displays: current P&L today, this week's win rate, user's stated reason for this trade
- 3-second display, skippable
- Cannot be permanently disabled (core behavioural feature)

**FR-012 — All-In Cost Transparency**
- Every order ticket shows: Broker fee + STT + GST + Exchange charges + Dhyan fee
- Single line: "Total charges: ₹X"
- No post-trade surprise

**FR-013 — Order Types**
- Market, Limit, Stop-Loss, Stop-Loss Market
- CNC (delivery), MIS (intraday), NRML (F&O)
- Advanced order types (bracket, cover) gated behind "Advanced Mode" in settings

---

### 4.5 Charts & Analytics
**FR-014 — Clean Chart Default**
- Candlestick chart, price + volume only by default
- Single AI-insight line beneath chart: "RSI is oversold — last 3 occurrences led to 4% rise in 5 days"
- Indicators hidden behind single "expand" tap
- Available indicators: RSI, MACD, Bollinger Bands, EMA, SMA, VWAP

**FR-015 — Inline Jargon Education**
- Every financial term in the app is tappable
- Tap → bottom sheet with 3 lines:
  1. What it is (plain language)
  2. What it means right now for this stock
  3. What most traders do at this level
- Replaces external education entirely

---

### 4.6 Behavioural & Mental Health Layer
**FR-016 — Daily Trade Budget**
- Optional: user sets max trades per day
- App shows warning (not block) when limit hit
- Resets at midnight

**FR-017 — End-of-Day Journal**
- After market close (3:30 PM), optional push notification
- 3-tap emotion check (😐 😰 🔥) + one text field
- Auto-attached to that day's trade log
- Weekly summary generated from journal entries

**FR-018 — Revenge Trade Detection**
- If user places 3+ trades within 10 minutes after a loss
- App shows non-blocking card: "You've made 3 trades quickly after a loss. Take a breath?"
- User can dismiss — no force, no lecture

**FR-019 — Weekly Trading Report**
- Every Sunday evening push notification
- Plain language: "This week, your ₹5,000 in Infosys grew ₹180 (+3.6%). You made 2 trades and held position. Solid week."
- No charts required in notification, full report in app

---

### 4.7 Beginner Mode
**FR-020 — Simple Mode / Finance Mode Toggle**
- Simple Mode replaces all jargon with plain language
- Finance Mode for experienced users
- Per-screen toggle, remembers preference

**FR-021 — Confidence Indicators**
- Every action has a silent indicator:
  - 🟢 Common action — most users do this
  - 🟡 Less common — here's what it means
  - 🔴 Rarely done by beginners — are you sure?
- Non-judgmental, informational only

**FR-022 — Post-Trade Plain Language Card**
- After every trade: "You bought 5 Tata Motors at ₹850. If it reaches ₹900, you make ₹250. If it drops to ₹800, you lose ₹250."
- Three lines maximum
- Shown for 30 seconds, dismissable

**FR-023 — First Trade Checklist**
- For first real trade only:
  - What are you buying? (company name + one line about what they do)
  - Why? (user types reason — no judgment)
  - Exit plan? (target / stop-loss / long hold)
  - Total charges shown
- Skippable after first time

---

### 4.8 Fees & Monetisation
**FR-024 — Fee Model**
- Equity Delivery: ₹0 (always free)
- Intraday trades: ₹5 per executed order
- F&O trades: ₹5 per executed order
- Crypto: ₹5 per executed order
- Paper trades: Always free
- First 10 intraday/F&O trades per month: Free (beginner protection)

**FR-025 — Premium Subscription (Phase 3)**
- ₹99/month
- Includes: Advanced alerts, AI chart insights, tax P&L report, paper trading leaderboard, priority support
- Free tier permanently available with core features

---

## 5. Non-Functional Requirements

| Requirement | Target |
|---|---|
| App launch time | < 2 seconds |
| Portfolio load (cached) | Instant (stale-while-revalidate) |
| Order placement latency | < 500ms after confirmation |
| Uptime | 99.5% during market hours (9:00–15:30 IST) |
| Crash rate | < 0.1% of sessions |
| Offline capability | Portfolio viewable offline (last cached state) |
| Accessibility | WCAG 2.1 AA compliant |
| Platform support | Android 8.0+, iOS 14.0+ |
| Data residency | India (Mumbai region) |

---

## 6. Out of Scope (V1)

- Mutual fund integration
- IPO applications
- US/global stock markets
- Options strategy builder
- Automated/algo trading
- Social/copy trading
- Insurance products
- Robo-advisory

---

## 7. Success Metrics

| Metric | 6-month target | 12-month target |
|---|---|---|
| Total registered users | 10,000 | 1,00,000 |
| Day-30 retention | 15% (industry avg: 4.5%) | 25% |
| Average daily screen time | < 8 minutes | < 6 minutes |
| Paper-to-real conversion | 20% | 30% |
| App Store rating | 4.2+ | 4.5+ |
| Revenge trade interventions accepted | 40% | 50% |
| Support tickets/1000 users | < 5 | < 3 |

---

## 8. Design Principles

1. **Calm over engagement** — never optimise for time-in-app
2. **Transparency first** — show all costs, always
3. **Plain language default** — assume zero financial background
4. **One action per screen** — no decision paralysis
5. **Earn trust before asking for money** — free first, paid later
6. **Intercept, don't block** — behavioural nudges never prevent action
7. **India-first** — IST timezone, INR currency, Indian broker APIs, Hindi support

---

*Document Owner: CSIT Mumbai University Charity Initiative*  
*Next Review: After Phase 1 completion*
