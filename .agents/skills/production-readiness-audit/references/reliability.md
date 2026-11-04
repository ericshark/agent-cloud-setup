# Reliability & Resilience Checklist

Depth reference for runtime resilience. For each area: **what good looks like**, **what
to look for**, **how to remediate**.

---

## 1. Error handling & graceful degradation

**Good:** Errors are caught at the right layer, fail safe, surface useful internal detail
and safe external messages, and the system degrades partially rather than collapsing.

**Audit:**
- Empty catch blocks / swallowed exceptions: `grep -rniE "catch\s*\([^)]*\)\s*\{\s*\}"`
  and Python `except.*:\s*pass`.
- Are external errors generic (no stack traces/secrets to clients) while internal logs
  keep full context + a correlation id?
- Is there a global error boundary/handler (web framework, React error boundary, process
  `unhandledRejection`/`uncaughtException`)?
- Does a non-critical dependency failure (recommendations, analytics) take down a core
  flow, or degrade gracefully (feature off, cached value, default)?

**Remediate:** Catch narrowly and act (retry/fallback/propagate) — never silently
swallow; map internal errors to safe external responses; add a top-level handler;
identify critical vs. optional dependencies and degrade the optional ones.

---

## 2. Retry logic with backoff & idempotency

**Good:** Transient failures are retried with **exponential backoff + jitter** and a cap;
retried operations are **idempotent** so duplicates are harmless.

**Audit:**
- Retries with fixed/no delay or unbounded counts (retry storms / thundering herd)?
- Are only *transient/idempotent* operations retried? Are non-idempotent writes (charge
  card, send email, create order) protected by idempotency keys / dedup?
- Do retries respect `Retry-After` and an overall deadline/timeout budget?
- At-least-once delivery (queues/webhooks) handled with dedup on the consumer?

**Remediate:** Add capped exponential backoff with jitter; make write paths idempotent
(idempotency keys, upserts, dedup tables, conditional writes); set a total retry budget;
don't retry 4xx (except 429); design consumers to tolerate duplicates.

---

## 3. Circuit breakers & fallback behavior

**Good:** Calls to flaky dependencies trip a breaker after a failure threshold, fail fast
while open, and recover via half-open probing — with a defined fallback.

**Audit:**
- Do remote calls have **timeouts** at all? (No timeout is the #1 cascading-failure
  cause.) `grep -rniE "timeout"` and check HTTP/DB/RPC clients explicitly.
- Any circuit breaker / bulkhead isolation, or does one slow dependency exhaust the
  whole thread/connection pool?
- Defined fallback when a dependency is down (cached/last-known-good/default/queue)?

**Remediate:** Set aggressive, explicit timeouts on every network call; add circuit
breakers (resilience4j, Polly, opossum, Hystrix-style); isolate dependencies with
bulkheads/separate pools; define and test fallbacks; add load shedding under overload.

---

## 4. Concurrency handling & race condition prevention

**Good:** Shared state is protected; check-then-act sequences are atomic; the data model
prevents lost updates.

**Audit:**
- Read-modify-write without locking/transaction (lost updates, double-spend)?
- Check-then-act races (e.g. "if not exists then create") — handled atomically?
- Optimistic (version column) or pessimistic locking where it matters?
- Unique constraints enforced in the DB, not just app code?
- Async/shared-memory hazards; non-thread-safe singletons; connection-pool sizing.
- Deadlock potential from inconsistent lock ordering.

**Remediate:** Use DB transactions with the right isolation level; optimistic
concurrency (version/ETag) or `SELECT ... FOR UPDATE`; DB unique constraints + handle the
conflict; atomic compare-and-swap; idempotent operations; consistent lock ordering;
prefer message queues to serialize contended work.

---

## 5. Caching strategy & invalidation

**Good:** Caching is deliberate (what, where, TTL, invalidation), and stale data has
bounded, acceptable impact.

**Audit:**
- What is cached and where (client, CDN, app, DB)? Are TTLs set intentionally?
- **Invalidation:** how does cached data get refreshed/purged on write? Is it correct?
- Cache stampede protection (locking, request coalescing, early recompute)?
- Negative caching of errors/empties? Per-tenant/per-user keying to avoid leakage?
- Cache failure mode: does a cache outage fail open (to origin) or take the app down?

**Remediate:** Document the caching layers and TTLs; pick an invalidation strategy
(write-through, TTL, event-based purge) and verify it; add stampede protection
(singleflight/locks/jitter); key caches to include tenant/user; ensure the app survives
a cache outage by falling back to the source.

---

## 6. Additions worth checking

- **Timeouts & deadlines:** every inbound request and outbound call has a timeout;
  deadlines propagate across hops (context cancellation).
- **Backpressure & queues:** bounded queues, load shedding, and rejection over unbounded
  growth/OOM; producer/consumer rate matching.
- **Health & readiness probes:** liveness vs. readiness distinguished; readiness gates
  traffic until dependencies are reachable.
- **Graceful shutdown:** SIGTERM handling — stop accepting new work, drain in-flight,
  close pools, finish within the grace period.
- **Resource limits:** connection-pool sizing, file descriptors, memory limits, and
  OOM behavior understood; no unbounded in-memory accumulation.
- **Clock & time:** UTC internally, timezone handled at edges, monotonic clocks for
  durations, leap-second/DST resilience.
- **Singletons of failure:** identify any component whose failure stops everything;
  decide if redundancy is warranted.
