# SEBI Disclosure Language — Dhyan

**Applicable Regulations:** SEBI (Investment Advisers) Regulations, 2013; SEBI (Research Analysts) Regulations, 2014; SEBI Circular on Algo Trading (Dec 2021)

---

## Standard Disclosure (To appear on all fee/trade screens)

### Order Confirmation Screen Disclosure
```
DISCLOSURE: Dhyan is a trading companion app and is NOT a SEBI-registered 
investment advisor, research analyst, or stockbroker. All trades are 
executed by your broker ([BROKER_NAME]). Dhyan charges a platform 
convenience fee of ₹5 per qualifying trade. This is separate from 
brokerage and statutory charges shown above. Investment in securities 
market is subject to market risks. Read all related documents carefully 
before trading.
```

### Fee Breakdown Template (Per Order Screen)
```
┌──────────────────────────────────────────┐
│         Fee Breakdown                    │
├──────────────────────────────────────────┤
│ Brokerage (Broker Name)     ₹XX.XX      │
│ STT                         ₹XX.XX      │
│ Exchange Txn Charges        ₹XX.XX      │
│ GST (18%)                   ₹XX.XX      │
│ SEBI Charges                ₹XX.XX      │
│ Stamp Duty                  ₹XX.XX      │
│ ──────────────────────────────────────── │
│ Dhyan Platform Fee          ₹5.00       │
│ GST on Platform Fee (18%)   ₹0.90       │
│ ──────────────────────────────────────── │
│ TOTAL CHARGES               ₹XX.XX      │
└──────────────────────────────────────────┘
```

---

## AI / Insights Disclaimer

### Chart Screen Disclosure (Beneath AI Insight Line)
```
ℹ️ This insight is generated using rule-based analysis of publicly 
available market data. It is NOT investment advice. Dhyan is not a 
SEBI-registered research analyst. Past patterns do not guarantee 
future performance. Always do your own research before making 
trading decisions.
```

---

## Paper Trading Disclosure

### Paper Trading Mode Banner
```
📋 PAPER TRADING MODE — You are trading with virtual money (₹1,00,000). 
No real money is involved. Paper trading results do not guarantee 
real trading performance. Market conditions, slippage, and liquidity 
in real trading may cause different outcomes.
```

---

## App-Wide Risk Disclosure

### Settings > Legal > Risk Disclosure Page
```
RISK DISCLOSURE

Trading and investment in securities market is subject to market risk. 
Past performance is not indicative of future performance. There is no 
guarantee of returns or protection against losses.

Dhyan is a technology platform that provides portfolio tracking, 
alerts, and paper trading simulation. Dhyan does not:
  • Provide investment advice or stock recommendations
  • Guarantee any returns on investments
  • Act as a stockbroker or sub-broker
  • Manage your portfolio on your behalf

All trading decisions are made by you. You are solely responsible 
for any profits or losses from your trading activity.

By using Dhyan for real trading, you acknowledge that:
  1. You understand the risks involved in securities trading.
  2. You are trading with your own broker account at your own risk.
  3. Dhyan's behavioural tools (warnings, budgets, journals) are 
     aids, not guarantees against loss.
  4. AI insights are rule-based observations, not recommendations.

For complaints or grievances, contact: [CONTACT_EMAIL]
SEBI Toll Free Helpline: 1800-266-7575
SEBI SCORES portal: https://scores.sebi.gov.in
```

---

## Compliance Notes for Development

1. **Every order confirmation screen** must display the fee breakdown with Dhyan's platform fee clearly separated from broker/statutory fees.
2. **AI insight disclaimers** must be visible without scrolling, directly beneath the insight text.
3. The **paper trading badge** must be clearly visible on every screen when in paper mode.
4. All disclosures must be available in both **English and Hindi** (Phase 4).
5. Fee disclosure language must be reviewed by a legal advisor before launch.

---

*This document is a template. All placeholders [IN_BRACKETS] must be replaced with actual entity details before deployment. Must be reviewed by a legal/compliance advisor.*
