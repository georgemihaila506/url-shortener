"""core.py — random_code + the collision-retry loop.

These are RED until you implement `random_code` and `shorten`. The retry tests use
a fake store (no DynamoDB) so they exercise the retry *policy* directly: how many
times you attempt, and what happens when attempts are exhausted.
"""

from __future__ import annotations

import pytest

from urlshortener import core
from urlshortener.core import ALPHABET, CODE_LENGTH
from urlshortener.db import CodeExists


def test_random_code_shape():
    code = core.random_code()
    assert len(code) == CODE_LENGTH
    assert all(c in ALPHABET for c in code)


def test_random_code_varies():
    # Astronomically unlikely to collide at 62^7 — this catches a constant/stub.
    assert len({core.random_code() for _ in range(100)}) > 1


class _FlakyStore:
    """Fake store: raises CodeExists for the first `fail_times` puts, then succeeds.

    Duck-types the one method `shorten` uses (`put_new`), so we test the retry
    policy without any AWS/DynamoDB.
    """

    def __init__(self, fail_times: int) -> None:
        self.fail_times = fail_times
        self.calls = 0
        self.saved: dict[str, str] = {}

    def put_new(self, code: str, long_url: str) -> None:
        self.calls += 1
        if self.calls <= self.fail_times:
            raise CodeExists(code)
        self.saved[code] = long_url


def test_shorten_retries_then_succeeds():
    store = _FlakyStore(fail_times=2)  # first 2 codes "collide", 3rd sticks
    code = core.shorten(store, "https://example.com", max_retries=5)
    assert store.calls == 3
    assert store.saved[code] == "https://example.com"


def test_shorten_raises_when_retries_exhausted():
    store = _FlakyStore(fail_times=99)  # every attempt collides
    with pytest.raises(RuntimeError):
        core.shorten(store, "https://example.com", max_retries=3)
    assert store.calls == 3  # tried exactly max_retries times, then gave up loudly
