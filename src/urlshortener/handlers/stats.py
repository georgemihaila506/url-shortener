"""GET /stats/{code} — return a link's click count + metadata. (M4)

A plain read of the analytics kept current by the redirect path (which bumps
`clicks` on every hit). 404 if the code is unknown.
"""

from __future__ import annotations

import json
import os

from ..db import UrlStore


def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body),
    }


def handler(event: dict, context: object) -> dict:
    """Return {code, long_url, clicks, created_at} for a code, or 404 if unknown.

    DynamoDB returns numbers as `Decimal` (which `json.dumps` can't serialize), so
    `clicks` and `created_at` are cast to `int`.
    """
    code = event["pathParameters"]["code"]
    store = UrlStore(os.environ["TABLE_NAME"])
    item = store.get(code)
    if item is None:
        return _response(404, {"error": "unknown code"})

    return _response(
        200,
        {
            "code": item["pk"],
            "long_url": item["long_url"],
            "clicks": int(item["clicks"]),
            "created_at": int(item["created_at"]),
        },
    )
