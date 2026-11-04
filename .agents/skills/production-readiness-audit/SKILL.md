---
name: production-readiness-audit
description: Audit, scan, and harden a codebase for production across security, reliability, testing, data/compliance, operations, and accessibility. Use when the user asks to security-check, security-scan, security-review, audit, harden, or assess production-readiness of a project; when checking for injection, auth/authz, secrets, TLS, rate limiting, dependency/supply-chain vulns, multi-tenancy isolation, PII/GDPR/HIPAA handling, audit logging, error handling, retries/idempotency, circuit breakers, race conditions, caching, tests/coverage/load/chaos testing, RTO/RPO/disaster recovery, observability/alerting, deploy safety/rollback, architecture diagrams/ADRs, or accessibility; or when asked to scaffold these controls, a threat model, DR plan, or audit report. Combines a stdlib-only scanner script with deep reference checklists and ready-to-fill templates.
---

# Production-Readiness Audit

## Overview

This skill turns Claude into a production-readiness reviewer that can **scan** an existing
codebase for risks, **review** changes against a comprehensive bar, and **create** the
missing controls and artifacts (threat models, DR plans, ADRs, audit reports). It spans
six dimensions: Security, Reliability, Testing/Process, Data & Compliance, Operations,
and Architecture/Accessibility.

The depth lives in `references/` (loaded on demand) and `assets/` (fill-in templates).
The `scripts/scan.py` scanner gives a fast, deterministic first pass with no dependencies.

## Choose the mode

1. **SCAN** — "security-check / scan / audit this project." Find risks across an existing
   codebase and produce a scored report.
2. **REVIEW** — "is this ready to ship?" / reviewing a diff or PR against the bar.
3. **CREATE** — "add rate limiting / write a threat model / set up a DR plan / generate
   the audit report." Scaffold a specific control or artifact.

Most real requests combine SCAN → then CREATE fixes. When the user is vague ("make this
secure"), default to SCAN first, present findings, then offer to fix.

## Scoping first (do this before a full audit)

Before a deep pass, establish scope so effort lands where it matters:
- **What & where:** which repo(s)/services/environments; the entry point(s) and stack.
- **Risk profile:** does it handle auth, money, PII/PHI, or multi-tenant data? Internet-
  facing? Regulated (GDPR/HIPAA/PCI)? This decides which references matter most.
- **Goal & depth:** quick triage vs. pre-launch gate vs. full audit report.

If the request is broad and the answers aren't obvious from the repo, ask 2–3 scoping
questions rather than auditing everything shallowly. For a narrow request ("check for
hardcoded secrets"), skip scoping and act.

## SCAN workflow

1. **Run the scanner** for a deterministic first pass:
   ```bash
   python3 scripts/scan.py <target-dir> --md report.md --json report.json
   ```
   - Stdlib-only; safe to run anywhere (no network, no writes outside the report files).
   - It detects stacks, flags secret/risk patterns with `file:line`, checks for expected
     hygiene files, and invokes installed external scanners (`npm audit`, `pip-audit`,
     `govulncheck`, `cargo audit`, `gitleaks`, `bundler-audit`) **only if present**.
   - Add `--strict` to exit non-zero on any HIGH finding (CI gate). `--no-tools` to skip
     external tools. Read the script to tune patterns for the project.
2. **Treat scanner output as leads, not verdicts.** Confirm each finding by reading the
   cited line — regex heuristics produce false positives (and miss things).
3. **Go deep with the references.** For each in-scope dimension, open the matching file
   below and work its "Audit" steps against the code. The references carry the real
   expertise; the scanner only points you there.
4. **Verify by reading code**, not by pattern-matching alone — especially authz/object
   ownership, tenant isolation, idempotency, and concurrency, which need human judgment.
5. **Write the report** using `assets/audit-report-template.md`: executive summary,
   scorecard, findings (severity + `file:line` + impact + fix), what's already good, and
   a prioritized remediation plan. Lead with the single biggest risk.

## REVIEW workflow (diff / PR / launch gate)

- Run the scanner on the changed paths; diff against the bar in
  `assets/production-readiness-checklist.md`.
- Focus on what the change touches: new endpoints (authz, input validation, rate limit),
  new dependencies (CVEs, license), data model changes (migrations, indexes, PII),
  new external calls (timeouts, retries, idempotency).
- Output: blockers (must-fix before merge) vs. follow-ups (track as issues).

## CREATE workflow (scaffold controls & artifacts)

Use the templates in `assets/` as starting points, then tailor to the stack:
- `audit-report-template.md` — the audit deliverable.
- `production-readiness-checklist.md` — drop-in PR/launch checklist.
- `threat-model-template.md` — STRIDE threat model.
- `disaster-recovery-plan-template.md` — RTO/RPO, backups, failover, drills.
- `incident-runbook-template.md` — on-call runbook.
- `adr-template.md` — Architecture Decision Record.

When implementing an actual control (e.g. adding rate limiting, idempotency keys, RLS,
security headers), read the relevant reference section first for the correct pattern, then
write code that matches the project's existing stack and conventions. Prefer vetted
libraries/managed services over hand-rolled security primitives.

## Reference map (load only what's in scope)

| Topic | Reference |
|---|---|
| Injection, authn/authz, sessions/tokens, secrets, TLS, rate limiting, dependency & supply-chain, multi-tenancy, audit logging, CSRF/SSRF/headers/encryption | `references/security.md` |
| Error handling, retries/backoff/idempotency, circuit breakers/timeouts, concurrency/races, caching/invalidation, backpressure, health checks, graceful shutdown | `references/reliability.md` |
| Unit/integration/E2E, regression, load/stress, chaos, coverage-in-CI, code review/CI gates, contract/mutation testing | `references/testing.md` |
| PII handling, retention/deletion, GDPR, HIPAA, PCI, consent, DSAR, encryption/keys, data residency | `references/data-and-compliance.md` |
| RTO/RPO, disaster recovery, backups, observability (logs/metrics/traces), SLO/alerting, deploy safety/rollback, on-call/incidents, cost guardrails | `references/operations.md` |
| Architecture diagrams (C4), ADRs, accessibility (WCAG 2.2 AA), docs, i18n, licenses | `references/architecture-and-accessibility.md` |

## Principles

- **Risk-first.** Rank by exploitability/impact; lead with the biggest risk; don't bury a
  HIGH under a list of style nits.
- **Evidence-based.** Every finding cites `file:line` or a concrete observation, with a
  concrete fix. No vague "improve security."
- **No false confidence.** State what was reviewed and what was not. Say when something
  needs runtime testing or legal/DPO confirmation rather than asserting compliance.
- **Defensive only.** This skill is for securing and hardening systems the user owns or is
  authorized to assess — not for crafting attacks against third parties.
- **Fix in the project's idiom.** Match existing conventions; prefer proven
  libraries/managed services to bespoke crypto/auth.
