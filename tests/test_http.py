import httpx

from jobradar.http import USER_AGENT, get_with_retry, make_client


def test_client_identifies_itself_and_has_timeouts():
    with make_client() as client:
        assert client.headers["user-agent"] == USER_AGENT and "JobRadar" in USER_AGENT
        assert client.timeout.read == 20 and client.timeout.connect == 10


def test_get_with_retry_recovers_from_transient_503(monkeypatch):
    calls = {"count": 0}

    def handler(request):
        calls["count"] += 1
        if calls["count"] < 3:
            return httpx.Response(503, request=request)
        return httpx.Response(200, json={"ok": True}, request=request)

    monkeypatch.setattr("jobradar.http.time.sleep", lambda _: None)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        resp = get_with_retry(client, "https://example.test")
    assert resp.status_code == 200
    assert calls["count"] == 3


def test_get_with_retry_honours_retry_after_with_a_cap(monkeypatch):
    waits = []
    answers = iter([("120", 429), ("2", 429), (None, 200)])

    def handler(request):
        retry_after, status = next(answers)
        headers = {"Retry-After": retry_after} if retry_after else {}
        return httpx.Response(status, headers=headers, request=request)

    monkeypatch.setattr("jobradar.http.time.sleep", waits.append)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert get_with_retry(client, "https://example.test").status_code == 200
    assert waits == [30.0, 2.0]


def test_get_with_retry_gives_up_and_raises(monkeypatch):
    monkeypatch.setattr("jobradar.http.time.sleep", lambda _: None)
    transport = httpx.MockTransport(lambda request: httpx.Response(503, request=request))
    with httpx.Client(transport=transport) as client:
        try:
            get_with_retry(client, "https://example.test")
        except httpx.HTTPStatusError as exc:
            assert exc.response.status_code == 503
        else:
            raise AssertionError("expected HTTPStatusError")
