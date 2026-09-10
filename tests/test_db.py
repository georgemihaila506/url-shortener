"""db.py against moto — proves the real DynamoDB conditional write behaves.

These pass already (db.py is written); they're the reference the retry loop trusts.
"""

from __future__ import annotations

import pytest

from urlshortener.db import CodeExists


def test_put_new_then_get(store):
    store.put_new("abc1234", "https://example.com")
    item = store.get("abc1234")
    assert item["long_url"] == "https://example.com"
    assert int(item["clicks"]) == 0


def test_put_new_rejects_duplicate_code(store):
    store.put_new("dup1234", "https://a.example")
    # Same code again -> the conditional write must fail (our uniqueness guarantee).
    with pytest.raises(CodeExists):
        store.put_new("dup1234", "https://b.example")


def test_get_missing_returns_none(store):
    assert store.get("nope999") is None


def test_increment_clicks_is_atomic(store):
    store.put_new("clk1234", "https://c.example")
    assert store.increment_clicks("clk1234") == 1
    assert store.increment_clicks("clk1234") == 2
