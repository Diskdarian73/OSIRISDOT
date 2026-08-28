"""Stdlib-only HTTP with retries, browser UA, and bounded parallelism.

No third-party dependencies by design: this skill has to run from a checkout
with nothing installed. urllib honours http_proxy/https_proxy from the
environment, so agent sandboxes work without extra configuration.
"""

import gzip
import io
import random
import ssl
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

# Reddit serves 403 to non-browser agents on every surface we use, so the
# browser UA is load-bearing rather than cosmetic.
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
API_UA = "osiris-recon/1.0 (+https://osirisexe.com)"

DEFAULT_TIMEOUT = 20
MAX_ATTEMPTS = 3
MAX_WORKERS = 6

_VERBOSE = False


def set_verbose(value: bool) -> None:
    global _VERBOSE
    _VERBOSE = value


def log(source: str, msg: str) -> None:
    """Progress goes to stderr so stdout stays a clean artifact stream."""
    if _VERBOSE:
        sys.stderr.write(f"[{source}] {msg}\n")
        sys.stderr.flush()


def _decode(resp: Any) -> str:
    raw = resp.read()
    if resp.headers.get("Content-Encoding") == "gzip":
        raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
    charset = resp.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace")


def get(
    url: str,
    *,
    ua: str = BROWSER_UA,
    accept: str = "*/*",
    timeout: int = DEFAULT_TIMEOUT,
    attempts: int = MAX_ATTEMPTS,
    source: str = "http",
) -> Optional[str]:
    """Fetch a URL, returning the body or None. Never raises.

    A returned None always means "this lane produced nothing" — callers treat
    a dead source as an empty source so one 403 can never sink a whole sweep.
    """
    last = ""
    for attempt in range(1, attempts + 1):
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": ua,
                "Accept": accept,
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return _decode(resp)
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            # 4xx other than rate-limiting will not change on retry.
            if e.code not in (429, 500, 502, 503, 504):
                break
        except (urllib.error.URLError, ssl.SSLError, TimeoutError, OSError) as e:
            last = type(e).__name__
        except Exception as e:  # noqa: BLE001 - a dead source must not crash a sweep
            last = type(e).__name__
            break
        if attempt < attempts:
            time.sleep(min(4.0, 0.6 * (2 ** (attempt - 1))) + random.uniform(0, 0.3))
    log(source, f"give up {url.split('?')[0]} ({last})")
    return None


def fan_out(
    jobs: Sequence[Tuple[str, Callable[[], Any]]],
    *,
    workers: int = MAX_WORKERS,
) -> Dict[str, Any]:
    """Run named callables in parallel. A raising job yields None, not a crash."""
    results: Dict[str, Any] = {}
    if not jobs:
        return results

    def run(item: Tuple[str, Callable[[], Any]]) -> Tuple[str, Any]:
        name, fn = item
        try:
            return name, fn()
        except Exception as e:  # noqa: BLE001
            log("fanout", f"{name} failed: {type(e).__name__}: {e}")
            return name, None

    with ThreadPoolExecutor(max_workers=min(workers, len(jobs))) as pool:
        for name, value in pool.map(run, jobs):
            results[name] = value
    return results
