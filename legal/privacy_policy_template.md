# Privacy Policy — Dhyan

**Last Updated:** [DATE]

**Dhyan** ("we", "our", "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our mobile application ("App") and backend services ("Services").

This policy is drafted in compliance with the **Digital Personal Data Protection Act, 2023 (DPDP Act)** of India.

---

## 1. Information We Collect

### 1.1 Personal Data
- **Phone Number:** Collected during registration for OTP-based authentication via Firebase Auth.
- **Name (Optional):** Collected during onboarding for personalisation.
- **Device Information:** Device model, OS version, and unique device identifiers for security (device binding, limited to 2 devices per account).

### 1.2 Financial Data
- **Broker OAuth Tokens:** Encrypted access tokens stored to connect your brokerage account. We **never** store your broker login credentials (username/password).
- **Trading Activity:** Order history, positions, and P&L data fetched from your connected broker account.
- **Paper Trading Data:** Virtual portfolio, orders, and performance data.

### 1.3 Behavioural Data
- **Journal Entries:** Optional trading journal notes and emotion tags you choose to record.
- **App Usage Patterns:** Screens visited, features used, and interaction patterns to improve the product. No keylogging or screen recording is performed.

### 1.4 Data We Do NOT Collect
- Aadhaar number, PAN card, or any government-issued identity documents.
- Bank account details or UPI IDs (payments are handled via Razorpay).
- Contact lists, photos, or any data unrelated to trading.

---

## 2. Purpose of Data Collection

We process your personal data for the following purposes under the DPDP Act:

| Purpose | Legal Basis (DPDP Act) |
|---|---|
| Account creation and authentication | Consent at registration |
| Executing trades via connected broker | Consent + contractual necessity |
| Displaying portfolio and P&L | Contractual necessity |
| Sending price alerts and notifications | Explicit consent (configurable) |
| Generating weekly trading reports | Legitimate interest |
| Improving app features and UX | Legitimate interest |
| Fraud prevention and security | Legitimate interest |

---

## 3. Data Storage and Security

- All personal data is stored on **encrypted PostgreSQL databases** hosted on secure cloud infrastructure.
- Broker OAuth tokens are encrypted using **AES-256** before storage.
- Data in transit is protected using **TLS 1.2+**.
- We implement rate limiting, input validation, and circuit breaker patterns to prevent abuse.
- Access to production databases is restricted and audited.

---

## 4. Data Sharing

We **do not sell** your personal data. Data is shared only with:

| Third Party | Purpose | Data Shared |
|---|---|---|
| Firebase (Google) | Authentication, Push Notifications, Crash Reporting | Phone number, device tokens, crash logs |
| Connected Broker (e.g., Angel One, Upstox) | Trade execution | Orders placed by you |
| Razorpay | Payment processing for platform fees | Transaction amount only |
| Sentry | Error monitoring | Anonymous error traces |

---

## 5. Your Rights Under the DPDP Act, 2023

As a **Data Principal**, you have the right to:

1. **Access:** Request a copy of all personal data we hold about you.
2. **Correction:** Request correction of inaccurate or incomplete data.
3. **Erasure:** Request deletion of your account and all associated data.
4. **Grievance Redressal:** File a complaint with our Data Protection Officer.
5. **Nominate:** Nominate another person to exercise your rights in case of death or incapacity.

To exercise any of these rights, contact us at **[CONTACT_EMAIL]**.

We will respond to all requests within **30 days** as required by the DPDP Act.

---

## 6. Data Retention

- **Active accounts:** Data is retained for the duration of your account.
- **Deleted accounts:** All personal data is permanently deleted within **90 days** of account deletion, except where retention is required by law (e.g., financial transaction records may be retained for up to 8 years under SEBI regulations).
- **Paper trading data:** Deleted immediately upon account deletion.

---

## 7. Children's Data

Dhyan is intended for users aged **18 and above**. We do not knowingly collect data from individuals under 18. If we become aware of such collection, we will delete the data immediately.

---

## 8. Changes to This Policy

We may update this Privacy Policy from time to time. We will notify you of material changes via in-app notification. Your continued use of the App after changes constitutes acceptance of the updated policy.

---

## 9. Contact Us

**Data Protection Officer:**
Name: [DPO_NAME]
Email: [CONTACT_EMAIL]
Address: [REGISTERED_ADDRESS]

**Grievance Officer (as per IT Act, 2000):**
Name: [GRIEVANCE_OFFICER_NAME]
Email: [GRIEVANCE_EMAIL]

---

*This document is a template and must be reviewed by a qualified legal advisor before publication.*
