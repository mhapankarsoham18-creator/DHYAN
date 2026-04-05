# Dhyan Application: Tier-1 Production Readiness Plan

This document represents the finalized, enterprise-grade roadmap to bring the Dhyan trading companion from a 23/100 prototype to a robust, compliant 95/100 production state.

This plan integrates **Premium Subscriptions (Razorpay/UPI)** and **Bank-Grade Security Architectures** required for financial data compliance. 

---

## 🏗️ Target Architectural Blueprints

1.  **Identity & Access**: Firebase Phone Auth + Firebase App Check (prevents API abuse from non-app clients).
2.  **Payments & Subscriptions**: Razorpay Subscription API + UPI Intent flows with cryptographically verified Webhooks.
3.  **Data Persistence**: PostgreSQL via Supabase/AWS RDS + Local Redis for caching & rate limiting.
4.  **Broker Interfacing**: Official Python SDKs (Shoonya, AngelOne) coupled with AES-256-GCM token encryption.

---

## Phase 1: Zero-Trust Security & Identity Foundation (Est: 3-5 Days)

**Objective**: Lock down the backend. Ensure requests are only coming from an untampered mobile app and authenticate users reliably.

### Sub-tasks
- [x] **1.1 Secret Lifecycle Management**
  - Delete `JWT_SECRET = "super-secret-key-12345"` and `os.urandom()` fallbacks.
  - Implement `.env` injection (dotenv). The app must crash (`sys.exit(1)`) if critical secrets are missing.
- [x] **1.2 Verified Authentication (Firebase Phone Auth)**
  - Integrate `google-services.json` on the client.
  - Wire Firebase Admin SDK in FastAPI to decode and verify the `id_token` against Google servers to prevent spoofing.
- [x] **1.3 Firebase App Check (Device Attestation)**
  - Integrate Play Integrity API (Android) / DeviceCheck (iOS) via Firebase AppCheck to ensure the backend only accepts requests from the genuine compiled app.
- [x] **1.4 WAF & Rate Limiting**
  - Wire up `slowapi` with Redis to rate-limit login endpoints and prevent brute-forcing.
- [x] **1.5 Supabase Postgres Migration**
  - Migrate `database.py` from SQLite to `postgresql+asyncpg` allowing connection to the managed Supabase Database instance.
  - Disable SQLAlchemy `echo=True` to prevent the leakage of PII and large transactional payload strings to the server logs.

---

## Phase 2: Billing Engine & Subscriptions (Est: 4-6 Days)

**Objective**: Monetize the application securely via Razorpay with support for UPI and recurring subscriptions.

### Sub-tasks
- [x] **2.1 Stripe/Razorpay Product Strategy**
  - Design the `Subscription` DB schema (`plan_id`, `status: active/past_due`, `current_period_end`).
  - Create Razorpay Plans (e.g., Free, Dhyan Pro).
- [x] **2.2 Payment Gateway Integration**
  - Write `razorpay_service.py` using `razorpay` Python SDK.
  - Expose `POST /api/v1/billing/create-subscription` (generates the order ID for the frontend).
- [x] **2.3 Secure Webhook Handling**
  - Expose `POST /api/v1/webhooks/razorpay`.
  - **CRITICAL**: Cryptographically verify the `X-Razorpay-Signature` header using the webhook secret to prevent artificial payment successes.
- [x] **2.4 Client-Side Flow**
  - Integrate `razorpay_flutter` package.
  - Handle success/failure callbacks and visually update the Profile settings to "Pro Active".
- [ ] **2.5 Payment Paper Trail & Accounting**
  - Generate programmatic invoices with GST details for all ₹5/trade or ₹99/month collections.
  - Ensure formal receipt generation to build tax-compliant records from day one.
- [ ] **2.6 Free Tier Device Fingerprinting**
  - Bind free tier quotas (e.g., 10 free trades/month) to unique device IDs instead of accounts.
  - Prevents "free tier abuse" via mass account generation.

---

## Phase 3: Data Integrity & Real Broker Engine (Est: 5-7 Days)

**Objective**: Implement rock-solid data layers and connect official Broker APIs.

### Sub-tasks
- [x] **3.1 Postgres Concurrent Locking**
  - Utilize Row-Level Locking (`SELECT FOR UPDATE`) on Postgres account balances to prevent race conditions during high-frequency trading.
- [x] **3.2 Bank-Grade Token Storage**
  - Encrypt all Broker Access Tokens in the DB using AES-256-GCM + HKDF (already scaffolded in `token_encryption.py`).
- [ ] **3.3 Broker SDK Integration** *(code scaffolded, never tested with live keys)*
  - Add `smartapi-python` (AngelOne) or Shoonya SDK (Note: strictly multi-user capable brokers; Zerodha is banned for multi-user).
  - Connect `POST /orders/place` to real APIs for executing equities.
  - **CRITICAL**: Implement robust Token Refresh Logic. Tokens expire daily; failing silently causes lost entries and furious users.
  - **CRITICAL**: Implement API Rate Limiting protection on polling engines to prevent the broker from permanently blocking the API key.
- [ ] **3.4 Live Socket Pipelining & Trade Validation** *(code scaffolded, never received a real tick)*
  - Demultiplex incoming broker WebSocket ticks through `price_relay.py`.
  - Deliver live LTP (Last Traded Price) directly to the Flutter UI via WebSockets.
  - **Order Input Validation:** Server-side hard validation on quantities (e.g., block QTY = -1 or 999999). Never trust the bare Flutter app payload.

---

## Phase 4: DevSecOps & Resilience (Est: 4 Days)

**Objective**: Prevent regressions and monitor the production landscape proactively.

### Sub-tasks
- [ ] **4.1 Test Automation Matrix** *(~25 tests written, coverage ~25%, target is 80%)*
  - Achieve >80% code coverage on the backend using `pytest` and `httpx`. Mock broker APIs and payment webhooks to ensure core domain logic holds.
  - Implement Frontend Widget testing for the Trade/Order placement funnel.
- [x] **4.2 SAST Vulnerability Scanning**
  - Integrate `bandit` in the pipeline to automatically scan for accidental secret leakage and unsafe queries.
- [x] **4.3 Observability (Sentry)**
  - Integrate Sentry on FastAPI to catch unhandled exceptions + DB deadlocks.
  - Integrate Sentry Flutter for UI crash tracking.
- [x] **4.4 CI/CD Pipelines**
  - Setup GitHub Actions / GitLab CI for automated testing prior to merge.
- [ ] **4.5 Disaster Recovery & Backups**
  - Enable Point-in-Time Recovery (PITR) on the Production Supabase Postgres instance to survive catastrophic data loss or accidental deletion.
- [ ] **4.6 Log Masking & PII Scrubbing**
  - Configure `logging` and Sentry to strictly mask PAN numbers, Passwords, and Auth Tokens so production logs cannot be exploited by internal threats.

---

## Phase 5: Last-Mile Polish & Delivery (Est: 2 Days)

**Objective**: Final UI adjustments, asset packing, and compliance cleanups.

### Sub-tasks
- [x] **5.1 Asset Bundling**
  - Download and embed the `Space Grotesk` and `Inter` font files locally so the premium aesthetic is consistent and offline-supported.
- [x] **5.2 Hardcode Elimination**
  - Wire the Notification center UI to a real `notifications` database table.
  - Ensure the "Connected Brokers" and "Funds" dashboard strictly compute from the DB.
- [ ] **5.3 Mandatory Legal Disclaimers (App Store Compliance)**
  - Hardcode persistent regulatory legal text across all analysis and UI screens: *"This is for informational purposes only. Not investment advice. Consult a financial advisor before investing."*
  - This is a mandatory requirement to survive Apple/Google App Store review algorithms.
- [ ] **5.4 Automated App Store Builds**
  - Configure Fastlane / GitHub Actions to securely build signed `.aab` (Android) and `.ipa` (iOS) files using securely vaulted keystores/certificates off-machine.

---

## Enterprise Exit Criteria (95/100)
1.  **Impenetrable Auth**: No hardcoded API keys/secrets; App Check enforces device safety; JWT verifications are solid.
2.  **Verified Payments**: Razorpay subscriptions securely mutate user roles via cryptographically validated webhooks.
3.  **Data Concurrency**: Postgres handles 100+ concurrent order requests without deadlocks.
4.  **Covered & Monitored**: Code coverage exceeds 80%, Sentry correctly traps test crashes.
