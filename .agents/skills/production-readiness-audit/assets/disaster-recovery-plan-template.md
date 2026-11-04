# Disaster Recovery Plan — <SERVICE / SYSTEM>

- **Owner:** <team>  **Last updated:** <YYYY-MM-DD>  **Last tested:** <YYYY-MM-DD>

> Store a copy of this plan somewhere reachable **when the primary system is down**
> (e.g. a separate wiki, printed, or a different cloud). A DR plan inside the failed
> system is useless.

## 1. Objectives

| Service / data store | RTO (max downtime) | RPO (max data loss) | Tier |
|---|---|---|---|
| | | | critical / high / normal |

## 2. Scenarios covered

- [ ] Data corruption / accidental deletion
- [ ] Database failure / loss
- [ ] Availability-zone outage
- [ ] Full region / provider outage
- [ ] Ransomware / malicious encryption
- [ ] Loss of secrets / key material
- [ ] Critical third-party dependency outage

## 3. Backups

| Store | Method | Frequency | Encrypted | Location(s) | Immutable copy | Restore-tested |
|---|---|---|---|---|---|---|
| | | | yes/no | | yes/no | <date> |

- **Backup of secrets/config/IaC:** <where, how>
- **Retention:** <how long backups are kept>
- **Restore procedure:** <step-by-step, with expected duration> — see runbook below.

## 4. Failover procedure

1. **Detect & declare** — <how an incident is detected; who declares DR; severity>.
2. **Communicate** — <status page, stakeholders, incident channel>.
3. **Fail over** — <DNS/traffic cutover, promote replica, switch region — exact steps>.
4. **Verify** — <health checks, smoke tests, data integrity checks>.
5. **Stabilize** — <scale, monitor, confirm SLOs>.

**DR-region dependency check:** confirm DNS, auth/IdP, secrets manager, and CI/CD are all
available in the recovery region.

## 5. Recovery runbooks

### Restore database from backup
1. …
2. …
**Expected duration:** <vs. RTO>

### Recover from ransomware (restore from immutable backup)
1. Isolate; 2. Identify clean restore point; 3. Restore to clean infra; 4. Rotate all
   secrets; 5. Verify integrity.

## 6. Roles & contacts

| Role | Person | Backup | Contact |
|---|---|---|---|
| Incident commander | | | |
| Database owner | | | |
| Cloud/infra | | | |
| Comms | | | |

## 7. Test schedule & history

| Date | Scenario | Result | RTO actual | RPO actual | Findings / actions |
|---|---|---|---|---|---|
| | | | | | |

> A DR plan is only real once it has been **tested**. Schedule the next drill.
