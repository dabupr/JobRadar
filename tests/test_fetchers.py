"""Every connector and feed must turn an HTTP error into an exception, never into empty data."""

from __future__ import annotations

import httpx
import pytest

from jobradar.connectors import CONNECTORS
from jobradar.feeds import FEEDS


def _client(status: int) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(status)))


@pytest.mark.parametrize("ats", sorted(CONNECTORS))
def test_connector_raises_on_http_error(ats):
    with _client(404) as client, pytest.raises(httpx.HTTPStatusError):
        CONNECTORS[ats]("acme", "Acme", client)


@pytest.mark.parametrize("feed", sorted(FEEDS))
def test_feed_raises_on_http_error(feed):
    with _client(503) as client, pytest.raises(httpx.HTTPStatusError):
        FEEDS[feed](client)
