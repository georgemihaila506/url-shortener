"""core.validate_url — ADR-0004 http(s)-only syntactic validation. RED until written."""

from __future__ import annotations

import pytest

from urlshortener.core import validate_url


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "https://example.com/path?q=1",
        "https://sub.example.co.uk/a/b#frag",
    ],
)
def test_accepts_http_and_https(url):
    assert validate_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "javascript:alert(1)",   # scheme injection — the footgun we're closing
        "data:text/html,<b>x",   # ditto
        "ftp://example.com",     # wrong scheme
        "example.com",           # no scheme
        "http://",               # no host
        "",                      # empty
        "https://" + "a" * 3000,  # over length cap
    ],
)
def test_rejects_everything_else(url):
    assert not validate_url(url)
