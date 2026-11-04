# Operations, Continuity & Observability Checklist

Depth reference for running the system in production: disaster recovery, observability,
safe deployment, and on-call. For each area: **what good looks like**, **what to look
for**, **how to remediate**.

---

## 1. RTO & RPO

**Good:** Recovery objectives are defined per service and validated by real drills.
- **RTO (Recovery Time Objective):** max tolerable downtime — how fast must it come back.
- **RPO (Recovery Point Objective):** max tolerable data loss — how much recent data may
  be lost (drives backup/replication frequency).

**Audit:**
- Are RTO/RPO numbers written down per critical service, agreed with the business?
- Does the architecture actually meet them (e.g. RPO of 5 min needs ≤5-min backup or
  continuous replication; daily backups imply up to 24h loss)?
- Have they ever been *measured* in a drill, or only assumed?

**Remediate:** Set RTO/RPO per service from business impact; align backup frequency and
replication topology to RPO; align failover automation to RTO; measure both in drills and
close the gap.

---

## 2. Disaster recovery plan

**Good:** A documented, tested DR plan covers data loss, region/provider outage, and
ransomware/corruption — with clear roles and runbooks. See
`assets/disaster-recovery-plan-template.md`.

**Audit:**
- **Backups:** automated, encrypted, **restore-tested** (a backup never restored is not a
  backup), stored off-site/cross-region, with immutable/air-gapped copies against
  ransomware. Backup of *all* critical stores (DB, object storage, config, secrets).
- **Failover:** documented procedure; multi-AZ/region as required; DNS/traffic cutover
  tested; dependencies (DNS, auth, secrets) available in the DR region.
- **Runbooks:** step-by-step recovery for top failure modes; contact/escalation list;
  not stored only in the system that's down.
- **Drills:** DR exercised on a schedule with findings fed back.

**Remediate:** Automate + encrypt backups and **schedule restore tests**; keep immutable
off-site copies; write failover and recovery runbooks; verify DR-region dependencies; run
periodic DR game days; keep runbooks accessible during an outage.

---

## 3. Observability: logging, metrics, tracing, alerting

**Good:** You can answer "is it healthy?" and "why is it broken?" quickly from telemetry
without shipping new code. The three pillars (logs, metrics, traces) are correlated.

**Audit:**
- **Structured logging** (JSON) with levels, timestamps, service, and a **correlation/
  request id** that threads across services? Secrets/PII excluded?
- **Metrics:** the four golden signals — latency, traffic, errors, saturation — per
  service? Business KPIs (signups, payments) monitored?
- **Distributed tracing** across service hops for latency attribution?
- **Alerting:** alerts on **symptoms users feel** (SLO burn, error rate, latency), not
  just CPU; actionable, low-noise, routed to on-call; runbook linked from each alert.
- **Dashboards** for each critical service; log aggregation/searchable; retention set.

**Remediate:** Adopt structured logging with correlation ids; emit the golden signals
(OpenTelemetry → Prometheus/Grafana/Datadog/etc.); add tracing; define SLO-based,
actionable alerts with runbook links; cut alert noise; build per-service dashboards.

---

## 4. SLI / SLO / error budgets

**Good:** Service Level Indicators (e.g. % of requests < 300ms, % non-5xx) and Objectives
(targets) are defined; error budgets govern the pace of change.

**Audit:** Are SLIs/SLOs defined and tracked? Is there an error budget and a policy for
when it's exhausted (slow down risky launches)?

**Remediate:** Define a few meaningful SLIs per critical journey; set realistic SLOs;
track burn; tie alerting and release decisions to the error budget.

---

## 5. Deployment safety & rollback

**Good:** Deploys are automated, gradual, reversible, and observable. A bad release is
caught early and rolled back fast.

**Audit:**
- **Rollback:** can you revert a release in minutes? Is the procedure tested? Are DB
  migrations backward-compatible (expand/contract) so app and schema can roll
  independently?
- **Progressive delivery:** canary / blue-green / rolling deploys with health gates, or
  big-bang? Automated rollback on health/SLO regression?
- **Feature flags:** risky changes behind flags with a documented kill switch?
- **Reproducible builds & environments:** IaC (Terraform/Pulumi), pinned images, parity
  across staging/prod?
- **Zero-downtime:** graceful shutdown + readiness probes + connection draining during
  deploys?

**Remediate:** Automate CI/CD with a fast, tested rollback; make migrations
expand/contract; adopt canary/blue-green with automated health-based rollback; put risky
features behind flags; manage infra as code; ensure graceful shutdown/draining.

---

## 6. On-call & incident response

**Good:** Someone is clearly responsible 24/7 for critical systems; incidents have a
defined process, and every significant one yields a blameless post-mortem with tracked
actions.

**Audit:**
- Defined on-call rotation + escalation path? Paging tied to actionable alerts?
- Incident severity levels, comms channels, and an incident-commander role defined?
- Blameless post-mortems with root-cause and **tracked** remediation items?
- Runbooks for common incidents (see `assets/incident-runbook-template.md`)?

**Remediate:** Establish on-call + escalation; define severity levels and an incident
process; run blameless post-mortems and track actions to completion; build runbooks.

---

## 7. Additions worth checking

- **Capacity & cost guardrails:** autoscaling configured and tested; budget alerts;
  quotas to prevent runaway spend (esp. serverless/LLM/API usage).
- **Configuration management:** config separate from code (12-factor); per-environment
  config; no prod config in the repo; config changes audited.
- **Dependency/SPOF mapping:** known single points of failure and their blast radius;
  graceful behavior when each upstream is down.
- **Data migration safety:** large/backfill migrations are batched, resumable, and
  reversible; tested on a prod-sized copy.
- **Environment parity & staging:** a staging environment that meaningfully resembles
  production for pre-release validation.
- **Time-to-detect / time-to-recover** tracked as reliability metrics over time.
