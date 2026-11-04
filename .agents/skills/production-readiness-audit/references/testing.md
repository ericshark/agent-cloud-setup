# Testing & Quality Checklist

Depth reference for test strategy and engineering process. For each area: **what good
looks like**, **what to look for**, **how to remediate**.

A useful mental model is the test pyramid: many fast unit tests, fewer integration
tests, a thin layer of end-to-end tests. Inverted pyramids (mostly slow E2E) are slow,
flaky, and expensive to maintain.

---

## 1. Unit, integration & end-to-end tests

**Good:** Each layer exists and tests the right thing — units test logic in isolation,
integration tests test seams (DB, queue, external API contracts), E2E tests test critical
user journeys through the real stack.

**Audit:**
- Do tests exist at all? `find . -type d -name "test*" -o -name "__tests__" -o -name spec`
- Distribution: is it a healthy pyramid or top-heavy/bottom-only?
- Are the **critical paths** (auth, payment, core domain action) covered end-to-end?
- Do tests assert behavior/outcomes, or just that code runs without throwing?
- Are external dependencies mocked at unit level but exercised for real (or via
  contract tests / testcontainers) at integration level?

**Remediate:** Fill the missing layer; prioritize tests on highest-risk/highest-churn
code; add E2E for the top few user journeys; replace "it doesn't crash" assertions with
outcome assertions.

---

## 2. Regression tests

**Good:** Every fixed bug gets a test that fails before the fix and passes after, so it
can't silently return.

**Audit:**
- Is "write a failing test first" part of the bug-fix workflow?
- Are there characterization tests around legacy code before refactors?

**Remediate:** Make a regression test mandatory in the bug-fix definition of done; add
characterization tests before touching untested legacy code.

---

## 3. Load & stress testing

**Good:** The system has known capacity limits, validated against expected and peak load,
with latency/throughput SLOs measured (p50/p95/p99).

**Audit:**
- Has load testing ever been done? Is there a tool/scenario (k6, Locust, Gatling, JMeter)?
- Are realistic peak and burst scenarios modeled (not just average)?
- Is stress/soak testing done to find the breaking point and memory leaks over time?
- Are results tied to capacity-planning and autoscaling thresholds?

**Remediate:** Build representative load scenarios; establish a performance baseline and
SLOs; run soak tests for leaks; load-test before major launches; track p95/p99, not
just averages; wire findings into capacity/autoscaling config.

---

## 4. Chaos engineering & resilience testing

**Good:** Failure modes (dependency down, latency injection, pod kill, zone loss) are
tested deliberately, ideally in production-like conditions with a blast-radius limit.

**Audit:**
- Are failure scenarios ever tested, or only assumed to work?
- Is there a hypothesis-driven practice (steady-state → inject → observe → learn)?
- Game days / failover drills run periodically?

**Remediate:** Start small in staging — kill a dependency, inject latency/errors,
verify timeouts/breakers/fallbacks actually fire; graduate to controlled production
experiments with monitoring and an abort switch; run periodic failover game days.

---

## 5. Test coverage thresholds enforced in CI

**Good:** Coverage is measured and a sensible floor is enforced in CI on changed code, so
quality can't silently erode — without gaming the metric.

**Audit:**
- Is coverage measured and reported? Is a threshold enforced or just displayed?
- Is the threshold on diff/patch coverage (more meaningful) or only global?
- Is coverage treated as a floor, not a target to game with assertion-free tests?

**Remediate:** Add coverage to CI with a realistic floor (e.g. 70–80% on changed lines);
prefer patch-coverage gates; pair coverage with mutation testing to check tests actually
assert; don't chase 100%.

---

## 6. Code review process & standards

**Good:** Every change is reviewed against a shared standard before merge; CI gates
(lint, type-check, tests, security scan) run automatically; main is protected.

**Audit:**
- Branch protection on main (required reviews + green CI)? Direct pushes blocked?
- Is there a review checklist / CONTRIBUTING / coding standard? Linter + formatter +
  type checker configured and enforced?
- Are PRs small enough to review well? Is there a CODEOWNERS for sensitive areas?
- Pre-commit hooks for secret scanning / formatting?

**Remediate:** Enable branch protection with required reviews and status checks; add
lint/format/type-check/test/security to CI; document standards in CONTRIBUTING.md; add
CODEOWNERS; keep PRs focused; add pre-commit hooks.

---

## 7. Additions worth checking

- **Contract testing:** consumer/provider contracts (Pact) for services/APIs so
  independent deploys don't break integrations.
- **Mutation testing:** (Stryker, mutmut, PIT) to verify tests fail when logic changes —
  the real measure of test quality.
- **Property-based testing:** (Hypothesis, fast-check) for invariants and edge cases.
- **Test data & environments:** reproducible fixtures/factories; no shared mutable test
  DB causing flakiness; production data not copied into test without masking.
- **Flaky-test management:** flakes tracked, quarantined, and fixed — not blindly retried.
- **Accessibility & visual regression tests** for UIs (axe, Playwright snapshots).
- **Static analysis / SAST** (Semgrep, CodeQL) in CI alongside tests.
