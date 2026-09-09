"""M0 smoke-test handler — proves the whole toolchain deploys and serves.

No logic; it just returns 200 with a JSON body so we can `curl` the live API
Gateway URL and confirm Terraform → Lambda → HTTP API works end to end before we
build anything real. Replaced by the shorten/redirect/stats handlers in M2+.
"""

from __future__ import annotations

import json


def handler(event: dict, context: object) -> dict:
    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(
            {"ok": True, "service": "url-shortener", "message": "hello from lambda"}
        ),
    }
