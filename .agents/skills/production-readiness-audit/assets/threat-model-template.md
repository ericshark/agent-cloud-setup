# Threat Model — <SYSTEM / FEATURE NAME>

- **Date:** <YYYY-MM-DD>  **Authors:** <names>  **Version:** <n>

## 1. Scope & assets

- **What we're modeling:** <system / feature boundary>
- **Assets to protect:** <data, credentials, money, availability, reputation…>
- **Trust boundaries:** <where data crosses from less-trusted to more-trusted: internet →
  edge → app → DB; tenant A → tenant B; user → admin>

## 2. Architecture & data flow

<Insert / link a data-flow diagram. List entry points (APIs, UIs, webhooks, queues,
admin), the data that flows, and where it is stored.>

| Entry point | Authn? | Data accepted | Downstream |
|---|---|---|---|
| | | | |

## 3. STRIDE analysis

For each component / data flow, walk the six categories. Record realistic threats only.

| # | Component / flow | STRIDE category | Threat | Likelihood × Impact | Mitigation | Status |
|---|---|---|---|---|---|---|
| 1 | | Spoofing | | | | open |
| 2 | | Tampering | | | | open |
| 3 | | Repudiation | | | | open |
| 4 | | Information disclosure | | | | open |
| 5 | | Denial of service | | | | open |
| 6 | | Elevation of privilege | | | | open |

**STRIDE → defenses (prompts):**
- **Spoofing** → authentication, MFA, mutual TLS, signed requests.
- **Tampering** → integrity checks, input validation, signed/immutable data, authz.
- **Repudiation** → audit logging, tamper-evident logs, request ids.
- **Information disclosure** → encryption (rest/transit), least privilege, redaction.
- **Denial of service** → rate limiting, quotas, timeouts, autoscaling, backpressure.
- **Elevation of privilege** → authz checks, least privilege, sandboxing, deny-by-default.

## 4. Top risks & decisions

1. <highest risk> → <decision: mitigate / accept / transfer / avoid> → <owner, date>
2. …

## 5. Residual risk

<Risks knowingly accepted, by whom, and why.>

## 6. Action items

| # | Action | Owner | Severity | Target date |
|---|---|---|---|---|
| 1 | | | 🔴🟡🟢 | |
