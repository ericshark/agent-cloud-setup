# production-readiness-audit

A [Claude](https://claude.com/claude-code) **Agent Skill** that turns Claude into a
production-readiness reviewer. It can **scan** a codebase for risks, **review** a change
against a comprehensive bar, and **create** the missing controls and artifacts — across
six dimensions:

- 🔐 **Security** — input sanitization & injection, authn/authz & roles, sessions & token
  expiry, secrets management, HTTPS/TLS & cert rotation, rate limiting & abuse prevention,
  dependency & supply-chain scanning, multi-tenancy & data isolation, audit & tamper-evident
  logging, plus CSRF/SSRF/security headers/encryption-at-rest/least-privilege.
- 🛡️ **Reliability** — error handling & graceful degradation, retries with backoff &
  idempotency, circuit breakers & fallbacks, timeouts, concurrency & race-condition
  prevention, caching & invalidation, backpressure, health checks, graceful shutdown.
- ✅ **Testing & process** — unit/integration/E2E, regression, load/stress, chaos &
  resilience, coverage thresholds in CI, code-review standards & CI gates, contract &
  mutation testing.
- 📄 **Data & compliance** — PII handling, retention & deletion, GDPR, HIPAA, PCI, consent,
  DSARs, encryption & key management, data residency.
- 🚀 **Operations** — RTO/RPO, disaster recovery & backups, observability (logs/metrics/
  traces), SLOs & alerting, deploy safety/rollback (canary/blue-green/feature flags),
  on-call & incident response, cost guardrails.
- 🏛️ **Architecture & accessibility** — architecture diagrams (C4), ADRs, WCAG 2.2 AA
  accessibility, docs, i18n, dependency licenses.

## What's inside

```
production-readiness-audit/
├── SKILL.md                       # the skill: modes, workflows, reference map
├── scripts/
│   └── scan.py                    # stdlib-only static scanner (no dependencies)
├── references/                    # deep checklists, loaded on demand
│   ├── security.md
│   ├── reliability.md
│   ├── testing.md
│   ├── data-and-compliance.md
│   ├── operations.md
│   └── architecture-and-accessibility.md
└── assets/                        # fill-in templates the skill produces
    ├── audit-report-template.md
    ├── production-readiness-checklist.md
    ├── threat-model-template.md          # STRIDE
    ├── disaster-recovery-plan-template.md # RTO/RPO, backups, failover
    ├── incident-runbook-template.md
    └── adr-template.md
```

## Install

Clone into your Claude Code skills directory:

```bash
git clone https://github.com/P1tak4s/production-readiness-audit.git \
  ~/.claude/skills/production-readiness-audit
```

Claude Code auto-discovers skills in `~/.claude/skills/`. Once installed, ask Claude to
"security-check", "audit", or "assess production-readiness of" a project and the skill
activates. You can also invoke it explicitly with `/production-readiness-audit`.

> Works with Claude Code, the Claude Agent SDK, and anywhere Agent Skills are supported.
> The skill itself is plain Markdown + a dependency-free Python script — portable by design.

## The scanner

`scripts/scan.py` is a fast, deterministic first pass. It is **stdlib-only**, makes **no
network calls**, and writes nothing outside the report files you choose.

```bash
# Markdown + JSON report for a project
python3 scripts/scan.py /path/to/project --md report.md --json report.json

# CI gate: non-zero exit if any HIGH-severity finding
python3 scripts/scan.py /path/to/project --strict --quiet

# Skip external tools (offline / fast)
python3 scripts/scan.py /path/to/project --no-tools
```

It detects the stack, flags secret/risk patterns with `file:line`, checks for expected
hygiene files (lockfile, CI, tests, `.gitignore`, license…), and — **only if they are
already installed** — runs `npm audit`, `pip-audit`, `govulncheck`, `cargo audit`,
`gitleaks`, and `bundler-audit` in read-only mode.

**The scanner reports leads, not verdicts.** Regex heuristics produce false positives and
miss things. The real depth is in the reference checklists; confirm every finding by
reading the cited code.

## Scope & ethics

This skill is **defensive**: for securing and hardening systems you own or are authorized
to assess. It is not for attacking third-party systems. Compliance sections are engineering
guidance, not legal advice — confirm regulatory obligations with counsel/your DPO.

## License

[MIT](LICENSE).

---

Built with [Claude Code](https://claude.com/claude-code) and its `skill-creator` skill.
