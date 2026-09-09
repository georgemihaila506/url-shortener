# ADR-0005 — M5 caching is a labeled learning exercise

**Status:** Accepted (grilled 2026-09-09)

## Context
The book flags URL shorteners as read-heavy and prescribes caching. But at this project's
real scale (personal), nothing is ever "hot" — DynamoDB on-demand + Lambda serve the
traffic untuned. The same YAGNI knife that rejected Snowflake (ADR-0001) applies.

## Decision
**Keep M5 caching, but honestly labeled as a learning exercise**, not a response to load.
We commit to **driving synthetic load** (`hey`/locust) so the cache can actually be
*observed* doing something. Cache the lookup **server-side** (in-Lambda memory vs DynamoDB
DAX; pick one) — never via browser 301 (that would defeat analytics, per ADR-0002).

## Consequences
- We learn the caching primitive without pretending it solves a real bottleneck.
- Verification requires manufactured load + before/after measurement (hit-rate, latency),
  with click counts still correct.
- If we won't drive load to observe it, we should defer M5 rather than cargo-cult it.

## Rejected
- **Keep caching unconditionally, unlabeled.** That's building machinery for contention we
  will never reach — the exact trap avoided with Snowflake.
