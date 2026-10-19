from __future__ import annotations

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
