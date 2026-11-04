# Security Checklist

Depth reference for the application-security dimensions. Each section lists **what good
looks like**, **what to look for when auditing**, and **how to remediate**. Use the
relevant sections; do not load the whole file unless doing a full security pass.

Grep starting points are given per section. Treat every grep hit as a lead to confirm,
not a verdict.

---

## 1. Input sanitization & injection prevention

**Good:** Untrusted input is validated at the boundary (type, length, range, format,
allow-list), and dangerous sinks use parameterization/encoding rather than string
building.

**Audit:**
- SQL: any query assembled by concatenation/f-strings/format with request data.
  `grep -rniE "(execute|query|raw)\(.*(\+|%|f\"|format\()" --include=*.py --include=*.js`
- OS commands: `shell=True`, `os.system`, `child_process.exec`, backticks.
- Template/SSTI: user input rendered through a template engine.
- Deserialization: `pickle.loads`, `yaml.load` (non-safe), Java `readObject`, PHP `unserialize`.
- Path traversal: user-controlled file paths joined without normalization/allow-list.
- XSS: `innerHTML`, `dangerouslySetInnerHTML`, `v-html`, unescaped server templates.
- Injection beyond SQL: NoSQL operators, LDAP, XPath, header/CRLF, log injection.

**Remediate:** Parameterized queries / prepared statements / ORM bindings; pass command
args as lists (never a shell string); context-aware output encoding; `yaml.safe_load`;
schema validation (zod, pydantic, JSON Schema) at the edge; canonicalize + allow-list
file paths; a Content-Security-Policy as XSS defense-in-depth.

---

## 2. Authentication, authorization, roles & permissions

**Good:** AuthN (who you are) and AuthZ (what you may do) are distinct, centralized, and
enforced server-side on every request. Authorization is checked at the object level, not
just the route level.

**Audit:**
- Are authz checks present on every state-changing endpoint, or only some?
- **IDOR / BOLA:** does the handler verify the current principal owns/may access the
  requested object id, or does it trust the id from the request? (OWASP API #1 risk.)
- Is there function-level authz (admin-only routes actually gated)?
- Role model: roles vs. fine-grained permissions; is it deny-by-default?
- Password storage: bcrypt/scrypt/argon2 with per-user salt — never MD5/SHA1/plaintext.
- MFA available for privileged accounts? Account lockout / throttling on login?
- Server-side enforcement (never trust client-side `isAdmin` flags or hidden fields).

**Remediate:** Centralize authz in middleware/policies; enforce object ownership checks;
deny-by-default; adopt RBAC or ABAC consistently; use a vetted auth library/IdP (OIDC)
rather than hand-rolled; hash passwords with argon2id/bcrypt; rate-limit + lock out
credential stuffing.

---

## 3. Session management & token expiry

**Good:** Sessions/tokens are short-lived, revocable, and bound to the client securely.

**Audit:**
- Cookies: `HttpOnly`, `Secure`, `SameSite` set? Session id regenerated on login
  (fixation defense) and invalidated on logout?
- JWTs: algorithm pinned (reject `alg: none`, reject algorithm confusion); short access
  TTL + refresh rotation; a revocation story (JWTs can't be un-issued — keep a denylist
  or keep them short). Are secrets/keys strong and rotated?
- Idle and absolute session timeouts defined?
- Tokens never logged, never placed in URLs/query strings.

**Remediate:** Set secure cookie flags; rotate session id on privilege change; pin JWT
alg and verify signature + `exp`/`aud`/`iss`; keep access tokens minutes-long with
rotating refresh tokens; implement server-side revocation for sensitive apps.

---

## 4. Secrets management

**Good:** No secret in source, config files, or images. Secrets come from a manager
(Vault, AWS/GCP/Azure secret manager, SOPS, Doppler) or runtime env, and are rotatable.

**Audit:**
- Hardcoded keys/passwords/tokens (run `scan.py`; consider `gitleaks`/`trufflehog`).
- `.env` committed to VCS? Secrets baked into Docker layers (`docker history`)?
- Secrets in CI logs, error messages, or client bundles?
- Rotation: is there a documented, tested rotation procedure? Last rotation date?

**Remediate:** Move secrets to a manager with least-privilege access; scrub from git
history (`git filter-repo`) and **rotate** anything exposed; add secret scanning to CI
(pre-commit + pipeline); separate secrets per environment; short-lived dynamic
credentials where possible.

---

## 5. HTTPS, TLS configuration & certificate rotation

**Good:** TLS everywhere (edge and service-to-service), modern config, automated renewal.

**Audit:**
- TLS verification ever disabled? `grep -rniE "verify\s*=\s*False|rejectUnauthorized.*false|InsecureSkipVerify.*true"`
- TLS version floor (1.2+, prefer 1.3); weak ciphers disabled; HSTS header set.
- Certificate renewal automated (ACME/cert-manager) with expiry monitoring/alerts?
- Internal traffic encrypted (mTLS) or assumed-trusted flat network?

**Remediate:** Enforce HTTPS + HSTS + redirect; disable TLS < 1.2 and weak ciphers;
automate issuance/renewal; alert ≥30 days before expiry; adopt mTLS for service mesh;
test with SSL Labs / `testssl.sh`.

---

## 6. Rate limiting & abuse prevention

**Good:** Expensive/abusable endpoints (login, signup, password reset, search, write,
AI/LLM, payments) are rate-limited per identity and per IP, with graceful 429s.

**Audit:**
- Any rate limiting at all? Where — edge, gateway, or app?
- Login/reset endpoints protected against brute force / enumeration?
- Bot defenses (CAPTCHA, proof-of-work, device fingerprinting) where warranted?
- Resource quotas to prevent one tenant starving others?

**Remediate:** Token-bucket/sliding-window limits keyed by user+IP; exponential backoff
responses with `Retry-After`; distinct limits per endpoint cost; WAF/edge protection for
L7 DDoS; uniform responses to avoid user enumeration.

---

## 7. Dependency scanning, supply chain & vulnerability patching

**Good:** Dependencies are pinned via lockfile, continuously scanned, and patched on a
defined SLA. Build provenance is verifiable.

**Audit:**
- Lockfile committed? Automated CVE scanning (npm/pip/cargo/go audit, Snyk, Dependabot,
  Trivy) in CI? Who watches the alerts?
- Patching SLA defined and met (e.g. critical ≤7 days)?
- **Supply chain:** lockfile integrity/hashes; pinned base images by digest; SBOM
  generated (CycloneDX/SPDX); signed commits/artifacts (sigstore/cosign); CI tokens
  least-privilege; protection against typosquatting/dependency-confusion.

**Remediate:** Commit lockfiles; enable Dependabot/Renovate; add `*-audit`/Trivy gates;
define and track a patch SLA; generate an SBOM; pin and scan container base images;
verify signatures; restrict and scope CI credentials.

---

## 8. Multi-tenancy & data isolation

**Good:** Every query and resource access is scoped to the tenant; cross-tenant access is
structurally impossible, not merely "we remember to filter."

**Audit:**
- Is `tenant_id` enforced at the data layer (RLS / mandatory scope) or only in app code?
- Shared caches/queues/search indexes keyed by tenant? Object storage paths isolated?
- Can a tenant id from the request be swapped to read another tenant's data (test it)?
- Noisy-neighbor protection (per-tenant quotas/limits)?

**Remediate:** Enforce isolation at the lowest layer possible (Postgres Row-Level
Security, separate schemas/DBs for high-assurance); include tenant scope in cache keys;
add automated cross-tenant access tests; per-tenant rate/resource quotas.

---

## 9. Audit trails & tamper-evident logging

**Good:** Security-relevant events (authn, authz failures, privilege changes, data
access/exports, admin actions) are logged immutably with who/what/when/where.

**Audit:**
- Are sensitive actions audited? Do logs include actor, action, target, timestamp,
  source IP, and request id?
- Are audit logs separated from app logs, append-only, and shipped off-host quickly?
- Tamper evidence: hash chaining, WORM storage, or signed log batches?
- Retention meets policy/regulation; secrets/PII are not logged.

**Remediate:** Emit structured audit events to a dedicated, append-only sink (or SIEM);
make them tamper-evident (hash-chain or write-once bucket); set retention per
requirement; redact PII/secrets; alert on anomalous audit volume or gaps.

---

## 10. Additions worth checking

- **CSRF:** state-changing form/cookie-auth endpoints carry anti-CSRF tokens or use
  SameSite + double-submit; pure token-auth APIs are typically exempt — confirm.
- **Security headers:** CSP, X-Content-Type-Options, X-Frame-Options/frame-ancestors,
  Referrer-Policy, Permissions-Policy.
- **Encryption at rest:** DB/disk/backup/object-store encryption; key management (KMS/HSM)
  with rotation; field-level encryption for the most sensitive data.
- **Least privilege / IAM:** scoped DB users, cloud roles, and CI tokens; no wildcard
  `*:*` policies; break-glass procedures audited.
- **SSRF:** server-side fetches of user-supplied URLs validated against an allow-list and
  blocked from cloud metadata endpoints (169.254.169.254).
- **File uploads:** type/size limits, content sniffing, stored off the web root or in a
  sandboxed bucket, served with safe content-type.
- **Error handling for security:** generic external errors (no stack traces/SQL to
  clients), detailed internal logs.
- **Threat model:** an explicit STRIDE pass exists for the system (see
  `assets/threat-model-template.md`).
