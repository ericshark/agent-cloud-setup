# Runbook — <INCIDENT TYPE, e.g. "API 5xx spike" / "Database CPU saturation">

- **Owner:** <team>  **Last reviewed:** <YYYY-MM-DD>  **Severity guidance:** <SEV1–3>

## Symptoms / how it pages
<What the alert says; what users experience; which dashboard shows it.>

## Quick triage (first 5 minutes)
1. Confirm scope: <which service/region/tenant; one user or all?>
2. Check dashboard: <link>  — golden signals (latency, errors, traffic, saturation).
3. Check recent changes: <deploys, flag flips, migrations, infra changes in last 1–2h>.
4. Declare severity and open an incident channel if user-facing.

## Diagnosis
- <Step: check X> → if <condition> → likely cause is <Y>, go to mitigation A.
- <Common cause 1> — how to confirm — how to fix.
- <Common cause 2> — how to confirm — how to fix.

## Mitigations (fastest safe action first)
- **Roll back** the last deploy: `<command / link>`.
- **Disable** the offending feature flag: `<flag>`.
- **Scale** <component>: `<command>`.
- **Shed load / enable rate limit:** `<how>`.
- **Failover:** see DR plan.

## Verify recovery
- <Smoke test / dashboard returns to baseline / error rate < threshold>.

## Communicate
- Update status page; notify stakeholders; post timeline in incident channel.

## After: post-mortem
- Schedule a **blameless** post-mortem within <N> days.
- Capture timeline, root cause, contributing factors, and **tracked** action items.
- Link the post-mortem here: <link>.

## Escalation
| When | Who | Contact |
|---|---|---|
| <unresolved in N min> | <secondary on-call / SME> | |
