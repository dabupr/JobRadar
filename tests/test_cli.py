from jobradar.cli import slug_variants


def test_slug_variants():
    assert slug_variants("Clarity AI")[:2] == ["clarityai", "clarity-ai"]
    assert slug_variants("Glovo")[0] == "glovo"


def test_check_server_error_is_a_warning(monkeypatch, capsys):
    import httpx

    from jobradar import cli

    def down(slug, name, client):
        request = httpx.Request("GET", "https://example.com")
        raise httpx.HTTPStatusError("boom", request=request, response=httpx.Response(503, request=request))

    def gone(slug, name, client):
        request = httpx.Request("GET", "https://example.com")
        raise httpx.HTTPStatusError("boom", request=request, response=httpx.Response(404, request=request))

    monkeypatch.setitem(cli.CONNECTORS, "down", down)
    monkeypatch.setitem(cli.CONNECTORS, "gone", gone)
    assert cli.run_check([{"name": "A", "ats": "down", "slug": "a"}], []) == 0
    assert "WARN 503" in capsys.readouterr().out
    assert cli.run_check([{"name": "B", "ats": "gone", "slug": "b"}], []) == 1
