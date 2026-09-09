# ADR-0002 — Redirect with 302 (temporary), not 301 (permanent)

**Status:** Accepted (grilled 2026-09-09)

## Context
`GET /{code}` returns an HTTP redirect to the long URL. 301 vs 302 is not cosmetic:
it decides whether we can see clicks and whether mappings are changeable.

## Decision
Return **302 Found (temporary)**. Every hit routes back through the service.

## Consequences
- **Click analytics (M4) works** — we observe every visit, so "a click" = every visit.
- **Mappings stay changeable/revocable** — no client caches a permanent answer.
- Cost: each redirect pays a Lambda + DynamoDB round trip (fine at our scale).
- **Read-path caching (M5) must be server-side** (in-Lambda / DAX). We must NOT rely on
  browser caching, because that is exactly what would hide the hits we want to count.

## Alternatives rejected
- **301 Permanent.** Browsers/proxies cache it hard → cheapest and fastest, but we go
  **blind to repeat clicks** (they never reach us) and "permanent" makes a mapping
  effectively immutable for cached clients. Incompatible with the analytics milestone.
