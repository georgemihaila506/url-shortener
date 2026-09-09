# ADR-0001 — Short-code generation: random base62 + conditional-write uniqueness

**Status:** Accepted (grilled 2026-09-09)

## Context
The short code *is* the primary key of a link. How we mint it decides enumerability,
write contention, and how much machinery we build. Target scale is a personal project
(≤ ~1M codes ever), deployed on scale-to-zero Lambda + DynamoDB.

## Decision
Generate a **random 7-character base62 code** (alphabet `[0-9A-Za-z]`, keyspace
62⁷ ≈ 3.5 trillion) and insert with a **conditional `PutItem`** (`attribute_not_exists(pk)`).
On the rare collision, regenerate and retry in a bounded loop. **DynamoDB is the
uniqueness referee** — no counter, no coordination.

At ~1M stored codes, collision probability per insert ≈ 1M / 3.5T ≈ 1-in-millions, so
retries are effectively never hit; the conditional write handles the theoretical case.

## Consequences
- Codes are **opaque / non-enumerable** — you cannot walk the corpus.
- **No write contention** — every insert is an independent key.
- The hands-on core to build becomes the **conditional-write + collision-retry loop**
  (a DynamoDB optimistic-concurrency lesson), not integer→base62 encoding.
- "Short" is fixed at 7 chars regardless of corpus size.

## Alternatives rejected
- **Sequential counter → base62.** Sequential ⇒ enumerable (walk /1,/2,/3 …); and a
  single hot counter item is the write bottleneck DynamoDB docs warn against.
- **Snowflake (distributed ID).** Built for a *fixed fleet of numbered servers*; a poor
  fit for scale-to-zero Lambda (no stable machine-id → collision risk or a self-built
  id-leasing coordinator), stays time-ordered/predictable, and yields longer ~11-char
  codes. Overengineering for this scale — DynamoDB already enforces uniqueness for free.
