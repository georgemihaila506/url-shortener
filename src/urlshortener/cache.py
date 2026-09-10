"""In-process read-through cache for redirect lookups (M5, ADR-0005).

Lambda reuses a warm execution environment between invocations, so a module-level
dict survives across requests handled by the same container — a free cache, no
extra infrastructure. Short codes are immutable (a code always maps to the same
URL), so cached entries never go stale: no invalidation needed. We cap the size
so memory can't grow without bound across many distinct codes.

LABELED LEARNING EXERCISE (ADR-0005): at personal scale nothing is truly hot; this
exists to learn the warm-container cache pattern, observed via synthetic load. The
paid alternative (DynamoDB DAX — a running cluster) is deliberately not used.
"""

from __future__ import annotations

from collections import OrderedDict

from .core import resolve

_MAX_ENTRIES = 1024
_cache: "OrderedDict[str, str]" = OrderedDict()

# Counters so the load driver can report a hit rate.
hits = 0
misses = 0


def cached_resolve(store, code: str) -> str | None:
    """Read-through cache over `resolve`: hit the store only on a cache miss.

    A hit returns the cached URL and marks it most-recently-used (LRU); a miss
    resolves from the store, caches a found URL (evicting the oldest once past
    `_MAX_ENTRIES`), and returns it — or None for an unknown code. Safe without
    invalidation because codes are immutable. `hits`/`misses` feed the load driver.
    """
    global hits, misses

    cached = _cache.get(code)
    if cached is not None:
        _cache.move_to_end(code)  # mark recently used
        hits += 1
        return cached

    misses += 1
    url = resolve(store, code)
    if url is None:
        return None  # unknown code — nothing to cache
    _cache[code] = url
    if len(_cache) > _MAX_ENTRIES:
        _cache.popitem(last=False)  # evict the oldest
    return url
