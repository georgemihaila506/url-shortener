"""cache.cached_resolve — read-through cache. RED until it's written.

Uses a counting fake store: the whole point is that a second lookup of the same
code does NOT call the store again.
"""

from __future__ import annotations

import pytest

from urlshortener import cache


class _CountingStore:
    """Counts get() calls. core.resolve() calls store.get() and reads long_url."""

    def __init__(self, mapping: dict[str, str]) -> None:
        self.mapping = mapping
        self.get_calls = 0

    def get(self, code: str):
        self.get_calls += 1
        url = self.mapping.get(code)
        return {"pk": code, "long_url": url} if url else None


@pytest.fixture(autouse=True)
def _reset_cache():
    cache._cache.clear()
    cache.hits = 0
    cache.misses = 0
    yield


def test_hit_avoids_second_store_read():
    store = _CountingStore({"abc1234": "https://x.example"})
    assert cache.cached_resolve(store, "abc1234") == "https://x.example"  # miss
    assert cache.cached_resolve(store, "abc1234") == "https://x.example"  # hit
    assert store.get_calls == 1  # the second lookup never touched the store
    assert cache.hits == 1
    assert cache.misses == 1


def test_unknown_code_returns_none():
    store = _CountingStore({})
    assert cache.cached_resolve(store, "missing") is None


def test_eviction_caps_size():
    n = cache._MAX_ENTRIES + 10
    store = _CountingStore({f"c{i}": f"https://e/{i}" for i in range(n)})
    for i in range(n):
        cache.cached_resolve(store, f"c{i}")
    assert len(cache._cache) <= cache._MAX_ENTRIES
