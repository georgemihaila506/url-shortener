# ADR-0003 — No deduplication of repeat URLs

**Status:** Accepted (grilled 2026-09-09)

## Context
When the same long URL is shortened twice, we either return the existing code (dedup)
or mint a new one. This decides the write path and the data model's core identity.

## Decision
**Mint a fresh code every time.** A short link is an **independent object** with its own
code and its own click count — it is *not* identified by its target URL. The write path
stays a single conditional `PutItem`.

## Consequences
- Two links to the same destination are distinct, each with independent analytics
  (correct for e.g. different campaigns pointing at one page).
- Slight storage "waste" (many codes → one URL) — irrelevant at personal scale.
- No reverse lookup needed.

## Alternatives rejected
- **Deduplicate to one code.** Requires a **reverse GSI** on `long_url` + an extra read
  on every shorten; forces a **URL-canonicalization policy** (utm params? trailing slash?
  http vs https? — a rabbit hole); and **collapses analytics** for links that share a
  target. Machinery and ambiguity we don't want.
