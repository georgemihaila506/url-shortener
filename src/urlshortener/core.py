"""Core shorten/resolve logic — AWS-agnostic and unit-testable.

DynamoDB details live in db.py; here we only orchestrate. The one piece with real
thinking is `shorten`'s **collision-retry loop** (ADR-0001): DynamoDB enforces
uniqueness on write, so we optimistically try a random code and regenerate on the
rare clash instead of coordinating or pre-checking.
"""

from __future__ import annotations

import secrets
import string

from .db import CodeExists, UrlStore

ALPHABET = string.ascii_letters + string.digits  # 62 chars → base62
CODE_LENGTH = 7
MAX_RETRIES = 5


def random_code(length: int = CODE_LENGTH) -> str:
    """Return a random `length`-char base62 code (unpredictable — uses `secrets`)."""
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def shorten(store: UrlStore, long_url: str, *, max_retries: int = MAX_RETRIES) -> str:
    """Allocate a unique code for `long_url`, persist it, and return the code.

    Optimistic concurrency (ADR-0001): try a random code, let DynamoDB's conditional
    write be the uniqueness referee, and regenerate on the rare `CodeExists` clash.
    After `max_retries` collisions (astronomically unlikely at 62⁷ ≈ 3.5T) we fail
    loudly rather than spin forever. Only `store.put_new` is used here, which is why
    this is testable with a fake store.
    """
    for _ in range(max_retries):
        code = random_code()
        try:
            store.put_new(code, long_url)
            return code
        except CodeExists:
            continue
    raise RuntimeError(f"could not allocate a unique code after {max_retries} attempts")


def resolve(store: UrlStore, code: str) -> str | None:
    """Return the long URL for `code`, or None if unknown."""
    item = store.get(code)
    return item["long_url"] if item else None
