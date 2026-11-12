from __future__ import annotations

import time

import httpx

from jobradar import __version__

USER_AGENT = f"JobRadar/{__version__} (+https://github.com/dabupr/JobRadar)"


def make_client() -> httpx.Client:
    """HTTP client used for every request: identifies itself, never waits forever."""
    return httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=httpx.Timeout(20, connect=10),
        follow_redirects=True,
        limits=httpx.Limits(max_connections=16),
    )


RETRY_STATUS = {429, 500, 502, 503, 504}
RETRY_DELAYS = (0.4, 0.8, 1.6)
MAX_RETRY_AFTER = 30.0  # never let one server stall a whole run for long


def _retry_after(response: httpx.Response, default: float) -> float:
    """Seconds to wait, honouring a numeric Retry-After header (capped)."""
    try:
        return min(MAX_RETRY_AFTER, max(default, float(response.headers["Retry-After"])))
    except (KeyError, ValueError):
        return default


def get_with_retry(client: httpx.Client, url: str, **kwargs) -> httpx.Response:
    """GET with a few retries for rate limits, server errors and network errors."""
    for delay in (*RETRY_DELAYS, None):
        try:
            response = client.get(url, **kwargs)
        except httpx.RequestError:
            if delay is None:
                raise
            time.sleep(delay)
            continue
        if response.status_code in RETRY_STATUS and delay is not None:
            time.sleep(_retry_after(response, delay))
            continue
        response.raise_for_status()
        return response
    raise AssertionError("unreachable")
