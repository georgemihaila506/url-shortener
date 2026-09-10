"""Observe the redirect cache under synthetic load (M5, ADR-0005).

Honest framing: at personal scale you won't see dramatic gains — this just
manufactures load so the warm-container cache has something to do. It hits the
redirect endpoint WITHOUT following the 302 (so we time our own endpoint, not the
target site) and reports latency percentiles. Expect the first hits (DynamoDB
read, maybe a cold start) to form the slow tail; warm cached hits cluster near min.

Usage:
    python scripts/loadtest.py https://<api>/<code> --n 200
"""

from __future__ import annotations

import argparse
import time
import urllib.error
import urllib.request


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None  # don't follow the 302 — time only our endpoint


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="a short-link URL, e.g. https://<api>/abc1234")
    ap.add_argument("--n", type=int, default=200, help="number of requests")
    args = ap.parse_args()

    opener = urllib.request.build_opener(_NoRedirect)
    latencies_ms: list[float] = []
    for _ in range(args.n):
        t0 = time.perf_counter()
        try:
            opener.open(args.url, timeout=10)
        except urllib.error.HTTPError:
            pass  # a 302/404 is expected; we still timed the round trip
        except Exception:
            continue
        latencies_ms.append((time.perf_counter() - t0) * 1000)

    if not latencies_ms:
        print("no successful requests")
        return
    latencies_ms.sort()

    def pct(q: float) -> float:
        return latencies_ms[min(len(latencies_ms) - 1, int(q * len(latencies_ms)))]

    print(
        f"n={len(latencies_ms)}  min={latencies_ms[0]:.0f}ms  p50={pct(.5):.0f}ms  "
        f"p90={pct(.9):.0f}ms  p99={pct(.99):.0f}ms  max={latencies_ms[-1]:.0f}ms"
    )


if __name__ == "__main__":
    main()
