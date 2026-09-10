"""GET /{code} — 302 redirect to the stored long URL. (M3)

Thin glue: pull the code from the path, resolve it, and either redirect (302) or
say 404. The redirect is *temporary* on purpose (ADR-0002) — every hit comes back
through us, which is what lets M4 count clicks and lets a mapping stay changeable.
"""

from __future__ import annotations

import json
import os

from ..core import resolve
from ..db import UrlStore


def handler(event: dict, context: object) -> dict:
    """YOUR CORE (M3): resolve a short code and redirect to its long URL.

    Steps:
      1. `code = event["pathParameters"]["code"]` — API Gateway fills this in from
         the `GET /{code}` route.
      2. `store = UrlStore(os.environ["TABLE_NAME"])`.
      3. `long_url = resolve(store, code)`.
      4. If it's None (no such code), return a 404 — e.g.:
           `{"statusCode": 404,
             "headers": {"content-type": "application/json"},
             "body": json.dumps({"error": "unknown code"})}`
      5. Otherwise return a **302** (ADR-0002, temporary):
           `{"statusCode": 302, "headers": {"location": long_url}}`
         The `location` header is what actually makes the browser navigate. Using
         302 (not 301) means the browser won't cache it, so every visit reaches us.
    """
    code = event["pathParameters"]["code"]
    store = UrlStore(os.environ["TABLE_NAME"])
    long_url = resolve(store, code)
    if not long_url:
        return {
            "statusCode": 404,
            "headers": {"content-type": "application/json"},
            "body": json.dumps({"error": "unknown code"}),
        }

    return {"statusCode": 302, "headers": {"location": long_url}}
