# Production-Readiness Audit — <PROJECT NAME>

- **Date:** <YYYY-MM-DD>
- **Auditor:** <name / "Claude">
- **Scope:** <repos / services / environments reviewed>
- **Commit / version:** <git sha or tag>

## Executive summary

<2–4 sentences: overall posture, the single biggest risk, and whether it is safe to
ship / operate as-is. Lead with the verdict.>

**Overall readiness:** 🔴 Not ready / 🟡 Conditional / 🟢 Ready
**Top 3 risks:**
1. <risk> — <impact>
2. <risk> — <impact>
3. <risk> — <impact>

## Scorecard

| Dimension | Status | Notes |
|---|---|---|
| Security — injection / input | 🔴🟡🟢 | |
| Security — authn / authz | 🔴🟡🟢 | |
| Security — sessions / tokens | 🔴🟡🟢 | |
| Security — secrets mgmt | 🔴🟡🟢 | |
| Security — TLS / transport | 🔴🟡🟢 | |
| Security — rate limiting | 🔴🟡🟢 | |
| Security — dependencies / supply chain | 🔴🟡🟢 | |
| Security — multi-tenancy / isolation | 🔴🟡🟢 | |
| Security — audit logging | 🔴🟡🟢 | |
| Reliability — error handling | 🔴🟡🟢 | |
| Reliability — retries / idempotency | 🔴🟡🟢 | |
| Reliability — circuit breakers / timeouts | 🔴🟡🟢 | |
| Reliability — concurrency / races | 🔴🟡🟢 | |
| Reliability — caching | 🔴🟡🟢 | |
| Testing — unit / integration / e2e | 🔴🟡🟢 | |
| Testing — load / stress | 🔴🟡🟢 | |
| Testing — chaos / resilience | 🔴🟡🟢 | |
| Testing — coverage in CI | 🔴🟡🟢 | |
| Process — code review / CI gates | 🔴🟡🟢 | |
| Data — PII / retention / deletion | 🔴🟡🟢 | |
| Compliance — GDPR / HIPAA / other | 🔴🟡🟢 | |
| Operations — RTO / RPO / DR | 🔴🟡🟢 | |
| Operations — observability / alerting | 🔴🟡🟢 | |
| Operations — deploy safety / rollback | 🔴🟡🟢 | |
| Architecture — diagrams / ADRs | 🔴🟡🟢 | |
| Accessibility — WCAG | 🔴🟡🟢 | |

## Findings

Each finding: severity, evidence (file:line or observation), impact, and remediation.

### 🔴 High (fix before shipping)
- **<title>** — `<file:line / location>`
  - **Impact:** <what an attacker/failure could do>
  - **Fix:** <concrete remediation>

### 🟡 Medium (fix soon)
- **<title>** — `<location>`
  - **Impact:** …
  - **Fix:** …

### 🟢 Low / informational
- <title> — <note>

## What's already good
<Call out existing strengths so they're preserved, not regressed.>

## Remediation plan

| # | Finding | Severity | Owner | Effort | Target date |
|---|---|---|---|---|---|
| 1 | | 🔴 | | S/M/L | |

## Appendix
- Tools run and versions (scan.py, npm audit, gitleaks, …)
- Areas explicitly **not** reviewed (and why)
- References consulted
