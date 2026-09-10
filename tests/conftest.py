"""Shared pytest fixtures. moto mocks DynamoDB in-process — no real AWS, no cost."""

from __future__ import annotations

import os

import boto3
import pytest
from moto import mock_aws

from urlshortener.db import UrlStore

# Dummy creds so boto3 doesn't hunt for real ones under the mock.
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_DEFAULT_REGION", "eu-north-1")

TABLE_NAME = "urls-test"


def _create_table(ddb):
    ddb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


@pytest.fixture
def store():
    """A UrlStore backed by a fresh moto DynamoDB table (created + torn down per test)."""
    with mock_aws():
        ddb = boto3.resource("dynamodb", region_name="eu-north-1")
        _create_table(ddb)
        yield UrlStore(TABLE_NAME, dynamodb=ddb)


@pytest.fixture
def api_env(monkeypatch):
    """moto table + TABLE_NAME env — for handler tests, which build their own store
    from the environment (as the real Lambda does), so nothing is injected."""
    monkeypatch.setenv("TABLE_NAME", TABLE_NAME)
    with mock_aws():
        ddb = boto3.resource("dynamodb", region_name="eu-north-1")
        _create_table(ddb)
        yield
