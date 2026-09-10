"""POST /shorten — validate a URL, mint a short code, return it. (M2)

Thin by design: parse the API Gateway request, delegate to core, shape the HTTP
response. The real logic (validation, retry) lives in core.py and is tested there
without API Gateway; this handler is just the glue, tested with a synthetic event.
"""

from __future__ import annotations

import json
import logging
import os

from ..core import shorten, validate_url
from ..db import UrlStore

logger = logging.getLogger(__name__)


def _response(status: int, body: dict) -> dict:
    """Shape an API Gateway (HTTP API v2) proxy response."""
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body),
    }


def handler(event: dict, context: object) -> dict:
    """Turn a POST /shorten request into a stored short link.

    201 {short_url, code} on success; 400 for a malformed body or an unacceptable
    URL (ADR-0004); 500 if allocation unexpectedly fails.
    """
    # A malformed body is the client's mistake — a 400, not a 500 crash.
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"error": "request body must be valid JSON"})

    url = body.get("url")
    if not isinstance(url, str) or not validate_url(url):
        return _response(400, {"error": "provide a valid http(s) url"})

    # Anything that goes wrong persisting (DynamoDB error, retries exhausted)
    # becomes a clean 500 with a logged stack trace — never a leaked one.
    try:
        store = UrlStore(os.environ["TABLE_NAME"])
        code = shorten(store, url)
    except Exception:
        logger.exception("failed to shorten url")
        return _response(500, {"error": "could not create short link"})

    domain = event["requestContext"]["domainName"]
    short_url = f"https://{domain}/{code}"
    return _response(201, {"short_url": short_url, "code": code})
