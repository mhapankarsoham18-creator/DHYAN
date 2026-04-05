# Tier-1 Zero to Ninety Tasks

## Phase 1: Zero-Trust Security & Identity
- [x] Remove hardcoded secrets (`auth_service.py`, `token_encryption.py`)
- [x] Implement strict `.env` loading containing system exit on fail
- [ ] Prompt user for `google-services.json` to fix Firebase initialization
- [x] Setup Firebase Admin SDK on the backend for JWT validation
- [x] Setup Firebase App Check (Play Integrity / DeviceCheck) to block non-app clients
- [x] Wire `slowapi` & Redis for Rate Limiting login endpoints
- [x] Refactor `get_current_user` to use proper `Depends(get_db)`
- [x] Fix UUID string-casting crash bug (`int(user_id)`)
- [x] Migrate `database.py` connection to `postgresql+asyncpg` for Supabase Postgres

## Phase 2: Billing Engine & Subscriptions (Razorpay)
- [ ] Construct Subscription & Plan schemas in the Database
- [ ] Generate Razorpay API Keys and create products/plans on Dashboard
- [ ] Develop `razorpay_service.py` with `create_subscription_order`
- [ ] Construct `POST /api/v1/webhooks/razorpay` endpoint
- [ ] Implement strict `X-Razorpay-Signature` validation
- [ ] Integrate `razorpay_flutter` sdk in UI 
- [ ] Handle Razorpay callbacks on the frontend (Success, Error, Wallet)

## Phase 3: Data Integrity & Real Broker Engine
- [ ] Run Alembic migrations for PostgreSQL
- [ ] Apply row-level locking (`SELECT FOR UPDATE`) on critical balance queries
- [ ] Encrypt all stored Broker API Tokens using AES-256-GCM
- [ ] Install AngelOne (`smartapi-python`) or Shoonya SDK
- [ ] Wire backend `price_relay.py` to Broker's WebSocket stream
- [ ] Subscribe Flutter to `ws://.../ws/prices`
- [ ] Connect `POST /orders/place` to real execution SDK methods

## Phase 4: DevSecOps & Resilient Test Coverage
- [ ] Write backend unit & integration tests with `pytest` (>80% cov)
- [ ] Write frontend widget tests for trade execution UI
- [ ] Integrate `bandit` in pipeline for static analysis (SAST)
- [ ] Setup Sentry SDK on FastAPI to trap exceptions & DB deadlocks
- [ ] Setup Sentry SDK in Flutter for UI crash reporting
- [ ] Create `.github/workflows` to gate PRs on test success

## Phase 5: Last-Mile Polish
- [ ] Bundle `Space Grotesk` and `Inter` TTF fonts in `pubspec.yaml`
- [ ] Scaffold `notifications` database table and endpoint
- [ ] Wire Flutter Notifications Screen to the actual endpoint
- [ ] Remove hardcoded "Connected Brokers" strings in profile UI
- [ ] Ensure application builds without terminal warnings
