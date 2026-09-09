# Request flows (activity diagrams)

The two core activities and the read-only stats path. These describe the
*designed* behavior — every branch traces back to a decision in [`adr/`](adr/):
random code + conditional-write retry (ADR-0001), 302 redirect (ADR-0002),
http(s)-only validation (ADR-0004). GitHub renders the Mermaid below inline.

## Shorten — `POST /shorten {url}`

The interesting part is the **collision-retry loop**: DynamoDB is the uniqueness
referee (a conditional `PutItem`), and on the rare clash we regenerate rather than
coordinate. Retries are bounded so a pathological case fails loudly, not forever.

```mermaid
flowchart TD
    A(["POST /shorten {url}"]) --> B{"http(s) URL &<br/>within length cap?"}
    B -- no --> E1["400 Bad Request"]
    B -- yes --> C["generate random<br/>7-char base62 code"]
    C --> D["PutItem<br/>condition: attribute_not_exists(pk)"]
    D --> F{"write succeeded?"}
    F -- yes --> H["201 Created<br/>{short_url}"]
    F -- "no — code already taken" --> G{"retries left?"}
    G -- yes --> C
    G -- no --> E2["500 Internal Error<br/>(retries exhausted)"]
```

## Redirect — `GET /{code}`

302 (not 301) so every hit reaches us: we count the click *and* keep the mapping
changeable. "A click" = every visit (ADR-0002).

```mermaid
flowchart TD
    A(["GET /{code}"]) --> B["GetItem by code"]
    B --> C{"found?"}
    C -- no --> E1["404 Not Found"]
    C -- yes --> D["atomic ADD clicks +1"]
    D --> F["302 Found<br/>Location: long_url"]
```

## Stats — `GET /stats/{code}`

```mermaid
flowchart TD
    A(["GET /stats/{code}"]) --> B["GetItem by code"]
    B --> C{"found?"}
    C -- no --> E1["404 Not Found"]
    C -- yes --> D["200 OK<br/>{clicks, long_url, created_at}"]
```
