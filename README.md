# URL Shortener on AWS

A small, real, deployable URL shortener — built to **learn Python + AWS** hands-on,
grounded in *System Design Interview* (Alex Xu) ch. 8. Serverless: **API Gateway →
Lambda → DynamoDB**, all defined in **Terraform**.

## The one idea

A short link is an **independent object** with its own random code and its own click
count — not a hash of its target. Uniqueness is enforced by the database on write
(DynamoDB conditional put), so we never need a central ID counter or a distributed ID
generator. Every other decision falls out of that and the **302 redirect** (so every
click is observable). The *why* for each choice lives in [`docs/adr/`](docs/adr/).

## Architecture

```
POST /shorten {url}  ─▶ API Gateway ─▶ Lambda(shorten)  ─┐
GET  /{code}         ─▶ API Gateway ─▶ Lambda(redirect) ─┤─▶ DynamoDB (urls)
GET  /stats/{code}   ─▶ API Gateway ─▶ Lambda(stats)    ─┘
```

- **Code:** random 7-char base62 (keyspace 62⁷ ≈ 3.5T), unique via conditional write (ADR-0001).
- **Redirect:** 302 temporary, so clicks are counted and mappings stay changeable (ADR-0002).
- **No dedup:** repeat URLs mint fresh independent links (ADR-0003).
- **Validation:** http(s)-only, length-capped (ADR-0004).

## Layout

```
src/urlshortener/   core.py  db.py  handlers/   # app (stdlib + boto3 only)
infra/                                          # Terraform (IaC)
tests/                                          # pytest + moto (no real AWS)
docs/               adr/  glossary.md  scale-estimate.md  flows.md
scripts/            package_lambda.py
```

## Setup (local)

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -e ".[dev]"           # editable install + test deps
pytest
```

Deploying needs the AWS toolchain (Terraform + AWS CLI + credentials) — see the
milestone notes; nothing is deployed without `terraform apply`.

## Status

Design hardened via a grilling session (ADR-0001…0005). **M0 — toolchain & scaffold**
in progress. Milestones M0→M7 tracked in the plan.
