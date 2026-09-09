"""Lambda entrypoints. Each module exposes a `handler(event, context)`.

Thin by design: parse the API Gateway event, call into core/db, shape the HTTP
response. Real logic lives in core.py / db.py so it's testable without AWS.
"""
