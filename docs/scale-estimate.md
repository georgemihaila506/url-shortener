# Scale estimate — the book's numbers vs ours

The book sizes for a hypothetical big service; we deliberately size for a **personal
learning project**. Recording both makes the gap explicit (and is why several "at scale"
features are learning exercises, not necessities).

## The book (Alex Xu, ch. 8)
- ~**100 M** URLs written per day → ~1160 writes/sec.
- Read:write ratio ~**10:1** → ~11.6 K reads/sec.
- Over **10 years** → ~**365 billion** records.
- Keyspace must exceed 365B: base62 length `n` with 62ⁿ ≥ 365B → **n = 7** (62⁷ ≈ 3.5T).

## Ours (personal)
- Writes: a handful per session, maybe **thousands total, ever**. Reads: similar order.
- Lifetime records: assume a generous ceiling of **~1 M**.
- Keyspace at **n = 7**: 62⁷ ≈ **3.5 trillion** — ~3.5M× our ceiling. Collision probability
  per random insert ≈ 1M / 3.5T ≈ **1 in 3.5 million** → retries effectively never occur
  (ADR-0001). We keep n = 7 (same as the book) for clean, non-guessable codes.

## Consequences for the design
- No hot partition, no throughput planning → DynamoDB **on-demand** is ample.
- Caching (M5) and rate limiting (M6) solve **no real problem at our scale** — kept as
  labeled learning exercises (ADR-0005), validated with synthetic load.
- The interesting engineering is **correctness + AWS wiring**, not throughput.
