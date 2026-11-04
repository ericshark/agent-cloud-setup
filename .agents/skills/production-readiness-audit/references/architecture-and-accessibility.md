# Architecture, Documentation & Accessibility Checklist

Depth reference for system documentation, decision records, and accessibility.

---

## 1. Architecture diagrams

**Good:** The system is documented at a level that lets a new engineer understand it
without reading all the code, and diagrams are kept current (ideally diagram-as-code).

**Audit:**
- Is there a current high-level architecture diagram (components, data stores, external
  dependencies, trust boundaries)?
- Are there data-flow diagrams showing where personal/sensitive data moves (these double
  as security trust-boundary maps for threat modeling)?
- Are diagrams versioned with the repo (Mermaid, PlantUML, Structurizr, diagrams.net
  source) rather than stale screenshots?
- Is the **C4 model** (Context → Container → Component → Code) or similar layering used so
  detail is appropriate per audience?

**Remediate:** Create a system-context and container diagram; add data-flow diagrams for
sensitive data; store diagrams as code in the repo so they update with changes; adopt C4
layering; review diagrams during significant changes.

---

## 2. ADRs (Architecture Decision Records)

**Good:** Significant, hard-to-reverse decisions are captured as short, immutable records
explaining context, the decision, and consequences — so the "why" survives team turnover.
See `assets/adr-template.md`.

**Audit:**
- Is there an `adr/` or `docs/decisions/` directory? Are major choices (datastore,
  framework, auth model, sync vs. async, build vs. buy) recorded?
- Do records capture **context and trade-offs**, not just the outcome? Are superseded
  ADRs marked rather than deleted?
- Is writing an ADR part of the workflow for consequential decisions?

**Remediate:** Adopt a lightweight ADR format (MADR/Nygard); backfill ADRs for the most
important existing decisions; record new significant decisions as they happen; mark
superseded ones with links to their replacements.

---

## 3. Accessibility (a11y)

**Good:** The product is usable by people with disabilities and conforms to **WCAG 2.2
Level AA** (the common legal/contractual baseline: ADA, Section 508, EN 301 549, the EU
Accessibility Act).

**Audit (POUR principles + practical checks):**
- **Perceivable:** text alternatives for images (`alt`); captions/transcripts for media;
  color contrast ≥ 4.5:1 for normal text; information not conveyed by color alone.
- **Operable:** full keyboard operability (no keyboard traps); visible focus indicators;
  logical focus order; skip-to-content link; targets large enough; no content that flashes
  > 3×/sec.
- **Understandable:** labels tied to inputs; clear, specific error messages; consistent
  navigation; language declared (`lang`).
- **Robust:** valid semantic HTML; ARIA used correctly (and only where native semantics
  don't suffice); works with screen readers (VoiceOver/NVDA/JAWS).
- **Tooling:** automated checks (axe, Lighthouse, pa11y) in CI catch ~30–40%; the rest
  needs manual keyboard + screen-reader testing.

**Remediate:** Fix contrast and alt text; ensure keyboard operability + visible focus;
use semantic HTML and correct ARIA; associate labels and write helpful error text; add
automated a11y tests to CI **and** schedule manual screen-reader/keyboard passes; target
WCAG 2.2 AA.

---

## 4. Additions worth checking

- **README & onboarding docs:** how to set up, run, test, and deploy; a new engineer can
  get productive without tribal knowledge.
- **API documentation:** OpenAPI/GraphQL schema published and current; versioning and
  deprecation policy.
- **Runbooks / operational docs:** see `operations.md` — the "how do I fix X at 3am" docs.
- **Internationalization (i18n):** if relevant — externalized strings, locale formatting,
  RTL support, Unicode-safe handling. (a11y and i18n often travel together.)
- **Dependency & license inventory:** licenses of dependencies are compatible with your
  distribution model.
- **Code ownership & bus factor:** critical areas have more than one person who
  understands them; CODEOWNERS reflects reality.
