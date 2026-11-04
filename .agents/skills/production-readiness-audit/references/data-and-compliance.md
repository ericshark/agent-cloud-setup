# Data Handling & Regulatory Compliance Checklist

Depth reference for personal-data handling and regulatory obligations.

> This is engineering guidance, not legal advice. Confirm obligations with counsel/your
> DPO. Requirements depend on jurisdiction, data types, and roles (controller/processor).

---

## 1. PII handling, data retention & deletion

**Good:** Personal data is inventoried, classified, minimized, encrypted, retained only
as long as needed, and deletable on request and on schedule.

**Audit:**
- **Data inventory / map:** is there a record of what personal data is collected, why,
  where it lives (DBs, logs, backups, analytics, third parties, caches), and who can
  access it? Without this, nothing else can be guaranteed.
- **Data classification:** is data tagged by sensitivity (public/internal/confidential/
  restricted, plus special categories like health/biometric)?
- **Minimization:** is only necessary data collected? Are free-text fields leaking PII?
- **Retention:** are there defined retention periods enforced by an automated job, or
  does data live forever by default?
- **Deletion:** can a specific subject's data be found and deleted across *all* stores,
  including backups, logs, search indexes, and downstream processors?
- **PII in logs:** check that emails, names, tokens, card/health data aren't logged.
  `grep -rniE "(email|ssn|credit_card|password|token)" --include=*.log` and log calls.

**Remediate:** Build/maintain a data map; classify and tag; minimize collection; implement
scheduled retention deletion; build a subject-deletion workflow covering every store
(define backup handling — e.g. crypto-shredding or documented backup-expiry); redact PII
from logs at the logging layer.

---

## 2. GDPR (and GDPR-like regimes: UK GDPR, CCPA/CPRA, LGPD)

**Good:** Lawful basis is established, data-subject rights are operationally supported,
and accountability is documented.

**Audit:**
- **Lawful basis** for each processing purpose (consent, contract, legitimate interest…).
- **Consent:** freely given, specific, opt-in (not pre-ticked), withdrawable as easily as
  given; consent records kept. Cookie/tracking consent before non-essential cookies.
- **Data-subject rights (DSAR):** access, rectification, erasure ("right to be
  forgotten"), portability (machine-readable export), objection/restriction — is each
  supported within the statutory window (generally 1 month)?
- **Records of Processing (RoPA)** maintained; **DPIA** done for high-risk processing.
- **Processors:** Data Processing Agreements with vendors/subprocessors; subprocessor
  list maintained.
- **International transfers:** SCCs/adequacy in place for data leaving the region; data
  residency honored.
- **Breach process:** can a notifiable breach be reported to the authority within 72
  hours? Is there a tested runbook?
- **Privacy by design & default:** privacy considered in design; defaults are the most
  privacy-protective.

**Remediate:** Document lawful bases and RoPA; implement compliant consent capture +
storage; build DSAR/export/erasure tooling; run DPIAs; sign DPAs and track
subprocessors; put transfer mechanisms in place; write and rehearse a 72-hour breach
runbook.

---

## 3. HIPAA (US protected health information)

**Good:** PHI is protected per the Security Rule's administrative, physical, and technical
safeguards; access is least-privilege and audited.

**Audit:**
- **Scope:** are you a covered entity or business associate? Are **BAAs** signed with all
  vendors touching PHI (cloud, email, analytics)?
- **Technical safeguards:** encryption of PHI at rest and in transit; unique user IDs;
  automatic logoff; access controls; **audit controls** logging PHI access.
- **Minimum necessary:** access limited to the minimum PHI needed per role.
- **Audit logging:** every PHI access/disclosure logged with who/what/when; logs retained
  (commonly 6 years) and reviewed.
- **Integrity & availability:** backups, disaster recovery, and contingency plan for PHI.
- **Breach notification:** process meeting HIPAA breach rules.

**Remediate:** Execute BAAs; encrypt PHI end-to-end; enforce least-privilege + unique
accounts + auto-logoff; implement comprehensive PHI access audit logging with long
retention; document policies, risk analysis, and a contingency/DR plan; train staff.

---

## 4. Audit trails & tamper-evident logging (compliance view)

See also `security.md` §9. For compliance specifically:
- Logs must answer **who accessed/changed which record, when, from where**.
- Retention must meet the longest applicable legal requirement.
- Logs must be protected from tampering and from unauthorized access (they often contain
  sensitive metadata).
- Be able to produce an audit report for a regulator/auditor on demand.

---

## 5. Additions worth checking

- **Encryption & key management:** at rest (DB/disk/backups/object store) and in transit;
  KMS/HSM-managed keys with rotation; crypto-shredding as a deletion strategy.
- **Data residency / sovereignty:** data stored/processed in required regions only.
- **Third-party / sub-processor risk:** inventory of who receives data and under what
  terms; security review of critical vendors.
- **Children's data:** COPPA/age-gating if minors may use the service.
- **PCI DSS:** if handling card data — prefer a tokenizing processor (Stripe/Adyen) to
  stay out of scope; never store raw PANs/CVV.
- **Anonymization vs. pseudonymization:** know which you actually achieve (re-
  identification risk); analytics datasets properly de-identified.
- **Right-to-export format:** portability exports are structured and machine-readable.
- **DSAR identity verification:** requesters are verified before data is returned/deleted.
