"""url-shortener — a learning URL shortener on AWS.

Package layout:
  core.py     — pure, AWS-agnostic logic (random code generation, validation)
  db.py       — DynamoDB access (conditional put, get, atomic click increment)
  handlers/   — thin Lambda entrypoints (shorten, redirect, stats)

Runtime dependencies are stdlib + boto3 only (boto3 ships in the Lambda runtime),
so the deploy artifact is a plain zip of this source. See docs/adr/ for the why.
"""
