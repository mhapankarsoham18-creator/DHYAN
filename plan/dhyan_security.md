# Dhyan — Security Engineering
**Classification:** Internal — Development Team Only  
**Version:** 1.0 | **Date:** March 2026  
**Standard:** OWASP Mobile Top 10 + OWASP API Security Top 10

---

## 0. Security Philosophy

Dhyan handles broker OAuth tokens, financial data, and real money transactions. A single security breach can result in:
- Unauthorised order placement on a user's broker account
- Personal financial data exposure
- Regulatory action under DPDP Act 2023 and SEBI guidelines
- Permanent loss of user trust

**Security is not a feature. It is a foundational requirement. Every component is designed with breach as the assumed default.**

Threat model summary:
- **Highest risk:** Stolen broker OAuth tokens used to place unauthorised trades
- **High risk:** Man-in-the-middle attacks on API calls
- **High risk:** Unauthorised access to app via stolen device
- **Medium risk:** SQL injection / API abuse
- **Medium risk:** Reverse engineering of APK to extract API keys

---

## 1. Authentication Security

### 1.1 Phone OTP via Firebase Auth
- OTP delivered via SMS (Firebase Auth)
- OTP validity: 5 minutes maximum
- OTP attempts: maximum 3 before 10-minute lockout
- Rate limiting: maximum 5 OTP requests per phone per hour
- Phone numbers stored hashed (SHA-256 + salt) in PostgreSQL — never plaintext

### 1.2 Session Management
- JWT access tokens: 15-minute expiry
- Refresh tokens: 7-day expiry, single-use (rotated on every refresh)
- All tokens invalidated on logout
- Concurrent session limit: 2 devices maximum per account
- New device login triggers notification to existing devices
- Session fingerprint includes: device ID, IP subnet, user agent

### 1.3 Device-Level Security
```dart
// Biometric + PIN gate on app open
final localAuth = LocalAuthentication();

Future<bool> authenticate() async {
  // Check if device is rooted (Android) or jailbroken (iOS)
  if (await isDeviceCompromised()) {
    showSecurityWarning(); // warn but don't hard block
  }

  return await localAuth.authenticate(
    localizedReason: 'Verify your identity to access Dhyan',
    options: const AuthenticationOptions(
      biometricOnly: false, // allow PIN fallback
      stickyAuth: true,
    ),
  );
}
```

### 1.4 Auto-Lock
- App locks after 5 minutes backgrounding
- App locks after 30 minutes inactivity in foreground
- Lock triggered immediately on app minimise (configurable to 1 min)
- Screenshot prevention enabled on all order and portfolio screens

```dart
// Prevent screenshots on sensitive screens
SystemChrome.setEnabledSystemUIMode(SystemUiMode.manual, overlays: []);
FlutterWindowManager.addFlags(FlutterWindowManager.FLAG_SECURE);
```

---

## 2. Broker Token Security

This is the most critical security domain. Broker tokens allow placing real trades on behalf of users.

### 2.1 Token Storage Architecture
```
User authenticates with broker (OAuth)
         │
         ▼
access_token (short-lived, ~1 day)
    → Stored in Redis with TTL matching token expiry
    → AES-256-GCM encrypted before storage
    → Key derived from: master_key + user_id (HKDF)

refresh_token (long-lived, ~30 days)
    → Stored in PostgreSQL
    → AES-256-GCM encrypted
    → Never sent to mobile client
    → Only used server-side for token refresh
```

### 2.2 Token Encryption Implementation
```python
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
import base64

MASTER_KEY = bytes.fromhex(os.environ["AES_MASTER_KEY"])  # 32 bytes, from env

def derive_key(user_id: str) -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=f"dhyan_broker_token_{user_id}".encode()
    )
    return hkdf.derive(MASTER_KEY)

def encrypt_token(token: str, user_id: str) -> str:
    key = derive_key(user_id)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce
    ciphertext = aesgcm.encrypt(nonce, token.encode(), None)
    return base64.b64encode(nonce + ciphertext).decode()

def decrypt_token(encrypted: str, user_id: str) -> str:
    key = derive_key(user_id)
    aesgcm = AESGCM(key)
    data = base64.b64decode(encrypted)
    nonce, ciphertext = data[:12], data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode()
```

### 2.3 Broker Token Never Reaches Mobile Client
```
Mobile App                   Backend
    │                            │
    │── "place order" ──────────►│
    │                            │── decrypt token from Redis
    │                            │── call broker API
    │                            │── forward order
    │                            │── receive confirmation
    │◄─ order confirmation ──────│
    │                            │
    ✗ broker token never sent to mobile
```

The mobile app never receives the broker access token. Orders are proxied through the backend. This means even if the mobile app is compromised, the attacker cannot directly call broker APIs.

### 2.4 Token Rotation & Revocation
- Access tokens refreshed proactively 5 minutes before expiry
- Token refresh failures → user notified to reconnect broker
- Broker disconnect → tokens immediately deleted from Redis + PostgreSQL
- Account deletion → all tokens wiped + secure delete (overwritten before deletion)
- Suspicious activity detected → all sessions + tokens revoked immediately

---

## 3. Mobile App Security

### 3.1 Certificate Pinning
Prevents man-in-the-middle attacks even with compromised root certificates.

```dart
// In dio setup
final dio = Dio();
dio.httpClientAdapter = IOHttpClientAdapter(
  createHttpClient: () {
    final client = HttpClient();
    client.badCertificateCallback = (cert, host, port) {
      // Pin our backend's certificate SHA-256 fingerprint
      final serverFingerprint = sha256.convert(cert.der).toString();
      return _allowedFingerprints.contains(serverFingerprint);
    };
    return client;
  }
);

// Pinned fingerprints (update on cert rotation)
const _allowedFingerprints = [
  "a3:4f:...", // Primary cert
  "b2:1e:...", // Backup cert (for rotation without downtime)
];
```

**Note:** Certificate pins must be updated in app when backend certificate rotates. Always pin 2 certificates (current + next) to enable rotation without app update.

### 3.2 Local Data Security
```dart
// All sensitive data via flutter_secure_storage
// Uses Android Keystore / iOS Secure Enclave
final storage = FlutterSecureStorage(
  aOptions: AndroidOptions(
    encryptedSharedPreferences: true,
    keyCipherAlgorithm: KeyCipherAlgorithm.RSA_ECB_OAEPwithSHA_256andMGF1Padding,
    storageCipherAlgorithm: StorageCipherAlgorithm.AES_GCM_NoPadding,
  ),
  iOptions: IOSOptions(
    accessibility: KeychainAccessibility.first_unlock_this_device,
    synchronizable: false, // do not sync to iCloud
  ),
);

// What gets stored in secure storage:
// - User's JWT refresh token
// - User's PIN hash (bcrypt)
// - Session fingerprint
// - User preferences (non-sensitive, but kept here for integrity)

// What is NEVER stored locally:
// - Broker OAuth tokens (backend only)
// - Bank/payment credentials
// - Plaintext passwords
```

### 3.3 Root / Jailbreak Detection
```dart
import 'package:flutter_jailbreak_detection/flutter_jailbreak_detection.dart';

Future<void> checkDeviceSecurity() async {
  final isJailbroken = await FlutterJailbreakDetection.jailbroken;
  final isDeveloperMode = await FlutterJailbreakDetection.developerMode;

  if (isJailbroken) {
    // Show warning — do not hard block (accessibility concern)
    // Log event to Sentry for monitoring
    // Disable biometric auth (use PIN only)
    // Increase session check frequency
    await _showSecurityWarning(
      "Your device may be modified. For your security, biometric login is disabled. Keep your PIN confidential."
    );
  }
}
```

### 3.4 APK Hardening (Android)
```gradle
// android/app/build.gradle
android {
    buildTypes {
        release {
            minifyEnabled true          // code obfuscation
            shrinkResources true        // remove unused resources
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt')

            // Prevent backup of app data to Google Drive
            // (prevents token extraction via backup)
        }
    }
}

// AndroidManifest.xml
<application
    android:allowBackup="false"
    android:fullBackupContent="false"
    android:networkSecurityConfig="@xml/network_security_config">
```

```xml
<!-- res/xml/network_security_config.xml -->
<!-- Enforce HTTPS everywhere, no cleartext traffic -->
<network-security-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
    <domain-config>
        <domain includeSubdomains="true">api.dhyan.app</domain>
        <pin-set>
            <pin digest="SHA-256">base64encodedpin1==</pin>
            <pin digest="SHA-256">base64encodedpin2==</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

### 3.5 iOS Security (Info.plist)
```xml
<!-- Prevent data inclusion in iCloud backup -->
<key>NSFileProtectionComplete</key>
<true/>

<!-- App Transport Security — HTTPS only -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
</dict>

<!-- Disable Pasteboard access for sensitive screens -->
<!-- Implemented in code on order and portfolio screens -->
```

---

## 4. Backend API Security

### 4.1 Authentication Middleware
```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Security(security)) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid token")
        # Verify token not in revoked list (Redis blacklist)
        if await redis.exists(f"revoked:{token}"):
            raise HTTPException(401, "Token revoked")
        return await get_user(user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.JWTError:
        raise HTTPException(401, "Invalid token")
```

### 4.2 Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, storage_uri=REDIS_URL)

# Per-endpoint limits
@router.post("/orders/place")
@limiter.limit("10/minute")   # max 10 order attempts per minute per IP
async def place_order(): ...

@router.post("/auth/otp/verify")
@limiter.limit("3/5minutes")  # max 3 OTP attempts per 5 minutes
async def verify_otp(): ...

@router.get("/portfolio")
@limiter.limit("30/minute")   # reasonable for real-time dashboard
async def get_portfolio(): ...
```

### 4.3 Input Validation
```python
from pydantic import BaseModel, validator, constr
from decimal import Decimal

class OrderRequest(BaseModel):
    symbol: constr(regex=r'^[A-Z0-9-]{1,20}$')  # whitelist: uppercase letters, numbers, dash only
    quantity: int
    price: Optional[Decimal]
    order_type: Literal["market", "limit", "sl", "sl-m"]
    product_type: Literal["CNC", "MIS", "NRML"]
    side: Literal["buy", "sell"]
    broker: Literal["angel_one", "upstox", "coindcx"]

    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0 or v > 100000:  # sanity cap
            raise ValueError('Invalid quantity')
        return v

    @validator('price')
    def price_must_be_positive(cls, v):
        if v is not None and (v <= 0 or v > 1000000):
            raise ValueError('Invalid price')
        return v
```

### 4.4 SQL Injection Prevention
```python
# ALWAYS use SQLAlchemy ORM or parameterized queries
# NEVER string-format SQL queries

# CORRECT
result = await db.execute(
    select(Order).where(Order.user_id == user_id)
)

# NEVER DO THIS
result = await db.execute(
    f"SELECT * FROM orders WHERE user_id = '{user_id}'"  # SQL injection risk
)
```

### 4.5 CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dhyan.app",        # production web (if applicable)
        "https://staging.dhyan.app"  # staging
        # NO wildcard (*) — never allow all origins
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### 4.6 Security Headers
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Force HTTPS
app.add_middleware(HTTPSRedirectMiddleware)

# Security headers on every response
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

---

## 5. Order Security — Anti-Fraud Layer

### 5.1 Order Validation Before Broker Forwarding
```python
async def validate_order_security(order: OrderRequest, user: User) -> bool:
    # 1. Verify user owns the broker connection being used
    connection = await get_broker_connection(user.id, order.broker)
    if not connection or not connection.is_active:
        raise SecurityException("Unauthorised broker connection")

    # 2. Sanity check: order value not exceeding reasonable limits
    quote = await get_quote(order.symbol)
    order_value = quote.ltp * order.quantity
    if order_value > 50_00_000:  # ₹50L sanity cap
        await notify_user_large_order(user, order_value)
        # Log for review, but don't block (user may be legitimate)

    # 3. Duplicate order detection (same symbol, qty, type within 5 seconds)
    recent_order = await get_recent_order(user.id, order.symbol, seconds=5)
    if recent_order and recent_order.matches(order):
        raise SecurityException("Duplicate order detected")

    # 4. Rate limit: max 10 orders per minute per user
    order_rate = await get_order_rate(user.id, minutes=1)
    if order_rate > 10:
        raise SecurityException("Order rate limit exceeded")

    return True
```

### 5.2 Order Audit Log
Every order attempt (successful or failed) logged immutably:
```python
class OrderAuditLog:
    id: UUID
    user_id: UUID
    timestamp: datetime
    action: str  # "place_attempt", "place_success", "place_failed", "cancelled"
    order_details: JSON  # symbol, qty, type, value
    ip_address: str  # hashed
    device_fingerprint: str  # hashed
    failure_reason: Optional[str]
    broker_response: Optional[str]
    # Audit logs are append-only, never deleted
```

---

## 6. Data Privacy (DPDP Act 2023)

### 6.1 Data Minimisation
Collect only what is necessary:

| Data | Collected | Reason |
|---|---|---|
| Phone number | Yes (hashed) | Auth |
| Email | Optional | Notifications |
| Name | No | Not needed |
| PAN / Aadhaar | No | Broker handles KYC |
| Bank details | No | Broker handles payments |
| Location | No | Not needed |
| Trade history | Yes | Core functionality |
| Journal entries | Yes | Core functionality |
| Device ID | Yes (hashed) | Session security |

### 6.2 Data Retention
```
User trade data: 7 years (SEBI requirement for financial records)
Journal entries: Until user deletes
Auth logs: 90 days
Audit logs: 3 years
Deleted account data: Purged within 30 days
Broker tokens: Deleted immediately on disconnect or account deletion
```

### 6.3 Right to Erasure
```python
async def delete_user_account(user_id: str):
    # 1. Revoke all active sessions
    await revoke_all_sessions(user_id)

    # 2. Delete all broker tokens (decrypt and shred)
    await delete_broker_connections(user_id)

    # 3. Delete Redis cache entries
    await redis.delete(f"portfolio:{user_id}")
    await redis.delete(f"session:{user_id}:*")

    # 4. Anonymise trade history (retain for SEBI, but unlink from identity)
    await anonymise_trades(user_id)

    # 5. Delete journal entries (user-generated content, no retention requirement)
    await db.execute(delete(JournalEntry).where(JournalEntry.user_id == user_id))

    # 6. Soft-delete user record (tombstone for audit trail)
    await db.execute(
        update(User).where(User.id == user_id).values(
            phone=None,
            email=None,
            deleted_at=datetime.utcnow()
        )
    )
```

---

## 7. Infrastructure Security

### 7.1 Render + Supabase (Backend)
- Environment variables injected at runtime via Render dashboard, never in code
- Supabase PostgreSQL: private connection string, not exposed publicly
- Automatic TLS for all Render endpoints
- Deploy from GitHub main branch only via Render auto-deploy
- UptimeRobot ping every 10 minutes to prevent Render free tier sleep during market hours

### 7.2 Database Security
```sql
-- Dedicated application user with minimal permissions
CREATE USER dhyan_app WITH PASSWORD 'strong_generated_password';
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO dhyan_app;
-- NO DROP, TRUNCATE, or DDL permissions for app user
-- Migrations run by separate dhyan_migrations user

-- Sensitive columns encrypted at application level
-- (broker tokens, phone numbers stored already encrypted)

-- Row-level security: users can only access their own data
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_orders ON orders
    USING (user_id = current_setting('app.current_user_id')::uuid);
```

### 7.3 Secrets Management
```
NEVER in code:      API keys, JWT secret, AES keys, DB passwords
NEVER in git:       .env files (gitignored), credential files
STORED IN:          Railway environment variables (encrypted at rest)
                    GitHub Actions secrets (for CI/CD)
ROTATION SCHEDULE:  JWT secret: 90 days
                    AES master key: 180 days
                    DB password: 90 days
                    Broker API secrets: Per broker policy
```

---

## 8. Security Monitoring & Incident Response

### 8.1 Alerts to Trigger Immediate Review
- More than 5 failed auth attempts from same IP in 10 minutes
- Order placed from new device (notify user)
- Order value > ₹5L
- Broker token used from backend IP not matching expected Railway IPs
- More than 20 API calls per second from single user
- Database query time > 5 seconds (possible injection attempt)

### 8.2 Sentry Integration
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,  # 10% of requests traced
    before_send=scrub_sensitive_data,  # remove tokens, phone numbers from events
)

def scrub_sensitive_data(event, hint):
    # Remove any token or credential data from Sentry events
    if "request" in event:
        headers = event["request"].get("headers", {})
        if "authorization" in headers:
            headers["authorization"] = "[FILTERED]"
    return event
```

### 8.3 Incident Response Playbook

**Scenario: Suspected broker token compromise**
1. Immediately revoke all active broker connections for affected user(s)
2. Notify affected users via SMS
3. Rotate AES master key
4. Re-encrypt all stored tokens with new key
5. Require all users to reconnect broker accounts
6. Investigate vector (audit logs)
7. File incident report

**Scenario: API abuse / DDoS**
1. Cloudflare (add in front of Railway for DDoS protection)
2. Tighten rate limits temporarily
3. Block offending IP ranges
4. Review and patch vulnerable endpoint

---

## 9. Security Checklist — Pre-Launch

### Mobile
- [x] Certificate pinning implemented and tested
- [x] Screenshot prevention on sensitive screens
- [x] Root/jailbreak detection active
- [x] Biometric + PIN auth working
- [x] No API keys or secrets in APK (verify with APKTool reverse engineering test)
- [x] ProGuard obfuscation enabled for release builds
- [x] `allowBackup=false` in AndroidManifest
- [x] App tested against OWASP MAS (Mobile Application Security) standard

### Backend
- [x] All endpoints require authentication (no unauthenticated routes except /auth/*)
- [x] Rate limiting on all sensitive endpoints
- [x] Input validation on all request models
- [x] SQL injection impossible (ORM only, no raw queries)
- [x] HTTPS enforced everywhere
- [x] Security headers on all responses
- [x] CORS whitelist, no wildcards
- [x] No debug endpoints or admin panels exposed to public internet

### Data
- [x] Broker tokens AES-256 encrypted at rest
- [x] Phone numbers hashed
- [x] No sensitive data in logs
- [x] No sensitive data in Sentry events
- [x] Database accessible only from Railway internal network

### Compliance
- [x] Privacy policy published
- [x] Terms of service published
- [x] Fee disclosure on every order screen
- [x] DPDP Act 2023 data processing requirements met
- [x] Right to erasure (account deletion) fully implemented

---

## 10. Dependency Security

```bash
# Run regularly in CI/CD pipeline

# Flutter
flutter pub outdated          # check for outdated packages
dart pub audit                # check for known vulnerabilities

# Python
pip-audit                     # check for known CVEs in dependencies
safety check                  # alternative CVE scanner

# Monthly manual review of:
# - Firebase SDK updates (security patches)
# - FastAPI + Starlette updates
# - Cryptography library updates (critical)
# - Broker SDK updates
```

**Rule:** All critical and high severity vulnerabilities patched within 48 hours of disclosure. Medium severity within 2 weeks.

---

*Document Owner: CSIT Mumbai University Charity Initiative*  
*Security Review: Completed before Phase 3 (real trading) deployment*  
*Penetration Test: Recommended before public launch (Phase 4)*
