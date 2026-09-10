"""GET /{code} — count the hit and 302-redirect to the stored long URL. (M4)

Thin glue: resolve the code, bump its click counter, and redirect. The redirect
is temporary (302, ADR-0002) precisely so every hit returns through here to be
counted — a 301 would let the browser cache it and hide repeat visits.
"""

from __future__ import annotations

import json
import os

from ..core import resolve
from ..db import UrlStore


def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body),
    }


def handler(event: dict, context: object) -> dict:
    """Resolve `code` and 302 to its long URL (counting the click), or 404."""
    code = event["pathParameters"]["code"]
    store = UrlStore(os.environ["TABLE_NAME"])
    long_url = resolve(store, code)
    if long_url is None:
        return _response(404, {"error": "unknown code"})
    store.increment_clicks(code)
    return {"statusCode": 302, "headers": {"location": long_url}}
