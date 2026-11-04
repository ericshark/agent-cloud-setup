# Production-Readiness Checklist

A copy-paste checklist for a PR, launch gate, or wiki page. Mark `[x]` when satisfied,
`[~]` when partial (add a note), `[ ]` when missing, `n/a` when not applicable.
Pair with the reference docs for the "how".

## Security
- [ ] Untrusted input validated at the boundary; parameterized queries; output encoded
- [ ] No injection sinks (`shell=True`, string-built SQL, unsafe deserialization, SSTI)
- [ ] AuthN centralized; passwords hashed (argon2/bcrypt); MFA for privileged users
- [ ] AuthZ enforced server-side on every request; object-level checks (no IDOR/BOLA)
- [ ] Sessions/cookies secure (HttpOnly, Secure, SameSite); tokens short-lived + revocable
- [ ] JWTs verify signature + claims; alg pinned (no `alg:none`/confusion)
- [ ] No secrets in code/config/images; managed + rotatable; secret scanning in CI
- [ ] HTTPS everywhere; TLS ≥1.2; HSTS; cert renewal automated + monitored
- [ ] Rate limiting / abuse protection on login, reset, signup, expensive endpoints
- [ ] Dependencies pinned (lockfile) + CVE-scanned in CI; patch SLA defined
- [ ] Supply chain: SBOM, pinned base images, signed artifacts/commits, scoped CI tokens
- [ ] Multi-tenant isolation enforced at the data layer (e.g. RLS); cross-tenant tested
- [ ] Security headers (CSP, X-Content-Type-Options, frame-ancestors, Referrer-Policy)
- [ ] CSRF protection where applicable; SSRF protections on server-side fetches
- [ ] Encryption at rest (DB/backups/object store) with managed keys + rotation
- [ ] Least-privilege IAM/DB roles; no wildcard policies
- [ ] Security-relevant events audited (tamper-evident); no PII/secrets in logs
- [ ] Threat model (STRIDE) exists for the system

## Reliability
- [ ] Errors handled (no silent swallow); safe external messages; global error handler
- [ ] Graceful degradation when optional dependencies fail
- [ ] Timeouts on every network/DB/RPC call
- [ ] Retries use exponential backoff + jitter + cap; only for transient/idempotent ops
- [ ] Non-idempotent writes protected by idempotency keys / dedup
- [ ] Circuit breakers / bulkheads for flaky dependencies; defined fallbacks
- [ ] Concurrency: races prevented (transactions, locking, DB unique constraints)
- [ ] Caching: TTLs + invalidation defined; stampede protection; survives cache outage
- [ ] Health/readiness probes; graceful shutdown with connection draining
- [ ] Bounded queues / backpressure / load shedding (no unbounded growth)

## Testing & process
- [ ] Unit + integration + E2E tests; critical paths covered E2E
- [ ] Regression test added for each fixed bug
- [ ] Load/stress testing done; capacity + p95/p99 latency known
- [ ] Resilience/chaos testing for key failure modes
- [ ] Coverage measured + threshold enforced in CI (ideally on changed code)
- [ ] CI gates: lint, type-check, tests, SAST, dependency scan
- [ ] Branch protection: required reviews + green CI; CODEOWNERS for sensitive areas

## Data & compliance
- [ ] Data inventory/map; data classified by sensitivity
- [ ] Data minimization; no PII in logs/analytics by accident
- [ ] Retention periods defined + enforced by automated deletion
- [ ] Subject deletion/export works across all stores (incl. backups, logs, indexes)
- [ ] GDPR: lawful basis, compliant consent, DSAR handling, RoPA, DPAs, transfers
- [ ] HIPAA (if applicable): BAAs, PHI encryption, access audit logs, min-necessary
- [ ] PCI (if applicable): use tokenizing processor; never store raw PAN/CVV
- [ ] Breach-notification runbook (e.g. GDPR 72h) exists and is rehearsed

## Operations
- [ ] RTO/RPO defined per critical service and validated in a drill
- [ ] Backups automated, encrypted, off-site, immutable copy, **restore-tested**
- [ ] DR plan documented, stored out-of-band, and exercised
- [ ] Structured logging with correlation ids; logs aggregated + retained
- [ ] Golden-signal metrics + dashboards; distributed tracing
- [ ] SLO-based, actionable alerting routed to on-call; runbooks linked
- [ ] Deploys gradual (canary/blue-green) with fast, tested rollback
- [ ] DB migrations backward-compatible (expand/contract)
- [ ] Risky changes behind feature flags with kill switch
- [ ] Infra as code; config separate from code; environment parity
- [ ] On-call rotation + escalation; blameless post-mortems with tracked actions
- [ ] Cost/quota guardrails + budget alerts

## Architecture, docs & accessibility
- [ ] Current architecture + data-flow diagrams (diagram-as-code in repo)
- [ ] ADRs for significant decisions
- [ ] README covers setup/run/test/deploy; API docs (OpenAPI/GraphQL) current
- [ ] Accessibility: WCAG 2.2 AA — contrast, alt text, keyboard, focus, semantics, ARIA
- [ ] Automated a11y checks in CI + manual screen-reader/keyboard testing
- [ ] i18n handled if relevant; dependency licenses compatible
