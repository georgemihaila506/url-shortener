# Glossary — first principles

Terms accrue as they come up. Two vocabularies: **AWS** (what we deploy on) and
**system design** (what the book teaches).

## AWS
- **Lambda** — run a function without managing a server; AWS spins up an ephemeral
  execution environment per demand and tears it down. Billed per request + run time;
  **scales to zero** (no traffic → no cost). Python runtime ships `boto3`.
- **Cold start** — the latency when Lambda must create a fresh environment (first call, or
  after scale-down) before running your code. Warm invocations reuse the environment.
- **API Gateway (HTTP API v2)** — the managed front door that maps HTTP routes
  (`POST /shorten`, `GET /{code}`) to Lambda integrations. HTTP API is the cheaper/simpler
  flavor vs the older REST API.
- **DynamoDB** — managed NoSQL key-value/document store. **On-demand billing** = pay per
  request, no capacity planning. A **conditional write** (`attribute_not_exists`) lets the
  DB reject a put that would overwrite — our uniqueness guarantee (ADR-0001).
- **GSI (Global Secondary Index)** — a secondary key layout over a table to query by a
  non-primary attribute. We deliberately avoid needing one (ADR-0003).
- **IAM role / policy** — *who* can do *what*. A Lambda assumes a **role**; least-privilege
  **policies** grant it only the DynamoDB actions it needs.
- **IaC / Terraform** — infrastructure as code: declare resources in files, `terraform
  apply` reconciles reality to match. State tracks what exists.

## System design
- **base62** — encode using `[0-9A-Za-z]` (62 symbols): URL-safe, compact. Here the code is
  *drawn* as random base62 chars, not an encoded integer (ADR-0001).
- **301 vs 302** — permanent (browser-cached, hides repeat hits) vs temporary (every hit
  returns to us, enables analytics). We use 302 (ADR-0002).
- **Read-heavy** — far more reads (redirects) than writes (shortens); motivates caching —
  which for us is a *labeled learning exercise* (ADR-0005), not a real bottleneck.
- **Optimistic concurrency** — don't lock; attempt the write and let it fail if a conflict
  occurred (our conditional put + retry), betting conflicts are rare.
