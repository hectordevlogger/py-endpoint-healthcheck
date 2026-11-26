# py-endpoint-healthcheck

Lightweight **Python** HTTP endpoint health and latency checker using the standard library with structured JSON output and unit tests.

## Run & Test

```bash
python checker.py [https://example.com](https://example.com)
python -m unittest discover -v

* `py-endpoint-healthcheck/checker.py`
```python
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from typing import Iterable, List
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class CheckResult:
    url: str
    ok: bool
    status_code: int | None
    latency_ms: float
    error: str | None = None


def check_endpoint(url: str, timeout: float = 5.0, user_agent: str = "py-endpoint-healthcheck/0.1") -> CheckResult:
    start = time.perf_counter()
    req = Request(url, headers={"User-Agent": user_agent}, method="GET")
    try:
        with urlopen(req, timeout=timeout) as resp:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            code = resp.getcode()
            return CheckResult(
                url=url,
                ok=200 <= code < 400,
                status_code=code,
                latency_ms=round(elapsed_ms, 2),
            )
    except HTTPError as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return CheckResult(
            url=url,
            ok=False,
            status_code=exc.code,
            latency_ms=round(elapsed_ms, 2),
            error=f"HTTP {exc.code}: {exc.reason}",
        )
    except URLError as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return CheckResult(
            url=url,
            ok=False,
            status_code=None,
            latency_ms=round(elapsed_ms, 2),
            error=f"Network error: {exc.reason}",
        )
    except TimeoutError:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return CheckResult(
            url=url,
            ok=False,
            status_code=None,
            latency_ms=round(elapsed_ms, 2),
            error="Request timed out",
        )


def run_checks(urls: Iterable[str], timeout: float = 5.0) -> List[CheckResult]:
    return [check_endpoint(url.strip(), timeout=timeout) for url in urls if url.strip()]


def to_json(results: List[CheckResult]) -> str:
    return json.dumps([asdict(r) for r in results], indent=2)


if __name__ == "__main__":
    import sys

    targets = sys.argv[1:]
    if not targets:
        print("Usage: python checker.py <url1> [url2 ...]", file=sys.stderr)
        sys.exit(1)

    output = run_checks(targets)
    print(to_json(output))