"""handlers.shorten — the POST /shorten glue, tested with a synthetic API GW event
and moto. RED until the handler is written."""

from __future__ import annotations

import json
import os

from urlshortener.core import resolve
from urlshortener.db import UrlStore
from urlshortener.handlers import shorten as shorten_handler


def _event(url, domain="abc.execute-api.eu-north-1.amazonaws.com"):
    """A minimal API Gateway (HTTP API v2) proxy event."""
    return {"body": json.dumps({"url": url}), "requestContext": {"domainName": domain}}


def test_shorten_returns_201_with_short_url(api_env):
    resp = shorten_handler.handler(_event("https://example.com/x"), None)
    assert resp["statusCode"] == 201
    body = json.loads(resp["body"])
    assert len(body["code"]) == 7
    assert body["short_url"].startswith("https://")
    assert body["short_url"].endswith("/" + body["code"])


def test_shorten_rejects_bad_url(api_env):
    resp = shorten_handler.handler(_event("javascript:alert(1)"), None)
    assert resp["statusCode"] == 400


def test_shorten_persists_the_mapping(api_env):
    resp = shorten_handler.handler(_event("https://persist.example"), None)
    code = json.loads(resp["body"])["code"]
    # Build a store the way the handler does; the code must resolve to the URL.
    store = UrlStore(os.environ["TABLE_NAME"])
    assert resolve(store, code) == "https://persist.example"


def test_shorten_rejects_malformed_json(api_env):
    event = {"body": "not json{", "requestContext": {"domainName": "d"}}
    resp = shorten_handler.handler(event, None)
    assert resp["statusCode"] == 400


def test_shorten_rejects_non_string_url(api_env):
    event = {"body": json.dumps({"url": 123}), "requestContext": {"domainName": "d"}}
    resp = shorten_handler.handler(event, None)
    assert resp["statusCode"] == 400
