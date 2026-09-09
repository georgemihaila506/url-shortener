# ADR-0004 — URL validation: syntactic http(s)-only

**Status:** Accepted (grilled 2026-09-09)

## Context
A shortener is a redirect machine and thus an abuse vector. `POST /shorten` must decide
what target URLs it accepts. Validation can be *syntactic* (well-formed?) or *semantic*
(safe/reachable?).

## Decision
**Syntactic only:** require a well-formed URL whose scheme is `http` or `https`, reject
all other schemes, and cap length. No safety/reachability checks.

## Consequences
- Kills the **scheme-injection footgun** (`javascript:`, `data:`, `file:` served from our
  own domain) in a few lines.
- Cheap and honest about what a learning project should own.
- We remain vulnerable to hosting phishing/malware *targets* — accepted, see below.

## Notes / rejected scope
- **SSRF is not a real risk here:** we issue a 302 and the *browser* fetches the target;
  our Lambda never requests it. Worth knowing *why* we're safe, not just that we are.
- **Phishing/malware blocklists** (Safe Browsing, reachability probes) — explicitly out of
  scope; a whole subsystem, not this project's lesson.
- **Blocking internal/private hosts** — considered; low value given the 302/browser-fetch
  model. May add later purely as defensive-coding practice.
