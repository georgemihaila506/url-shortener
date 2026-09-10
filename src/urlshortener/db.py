"""DynamoDB access for the URL store — the ONLY module that talks to AWS.

One table keyed by the short code (`pk`). Keeping all boto3 here lets core.py stay
AWS-agnostic and unit-testable (swap this out for a fake), and lets us test this
module against moto (a mock DynamoDB) without real AWS.
"""

from __future__ import annotations

import time

import boto3
from botocore.exceptions import ClientError


class CodeExists(Exception):
    """A conditional put failed because the short code is already taken."""


class UrlStore:
    def __init__(self, table_name: str, *, dynamodb=None) -> None:
        # `dynamodb` lets tests inject a moto-backed resource; prod uses the default.
        self._table = (dynamodb or boto3.resource("dynamodb")).Table(table_name)

    def put_new(self, code: str, long_url: str) -> None:
        """Insert a brand-new link. Raise `CodeExists` if `code` is already taken.

        `attribute_not_exists(pk)` makes this atomic and race-free: DynamoDB itself
        rejects the write if an item with this key already exists. That rejection —
        surfaced here as `CodeExists` — is our uniqueness guarantee (ADR-0001), so
        the caller never has to read-then-write (which would race).
        """
        try:
            self._table.put_item(
                Item={
                    "pk": code,
                    "long_url": long_url,
                    "created_at": int(time.time()),
                    "clicks": 0,
                },
                ConditionExpression="attribute_not_exists(pk)",
            )
        except ClientError as err:
            if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise CodeExists(code) from err
            raise

    def get(self, code: str) -> dict | None:
        """Return the item for `code`, or None if there's no such link."""
        return self._table.get_item(Key={"pk": code}).get("Item")

    def increment_clicks(self, code: str) -> int:
        """Atomically bump the click counter and return the new value (used in M4)."""
        resp = self._table.update_item(
            Key={"pk": code},
            UpdateExpression="ADD clicks :one",
            ExpressionAttributeValues={":one": 1},
            ReturnValues="UPDATED_NEW",
        )
        return int(resp["Attributes"]["clicks"])
