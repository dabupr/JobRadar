import httpx

import jobradar.cli as cli
from jobradar.cli import collect, main, slug_variants
from jobradar.models import Job


def test_slug_variants():
    assert slug_variants("Clarity AI")[:2] == ["clarityai", "clarity-ai"]
    assert slug_variants("Glovo")[0] == "glovo"


def test_collect_uses_configured_sources(monkeypatch):
    monkeypatch.setattr(
        "jobradar.cli.load_companies",
        lambda _: [{"name": "Acme", "ats": "lever", "slug": "acme"}],
    )
    monkeypatch.setattr("jobradar.cli.load_feeds", lambda _: ["remotive"])
    monkeypatch.setitem(
        cli.CONNECTORS,
        "lever",
        lambda slug, name, client: [Job("1", "Dev", name, "Remote", "https://x/1", "lever", remote=True)],
    )
    monkeypatch.setitem(
        cli.FEEDS,
        "remotive",
        lambda client: [Job("2", "Data", "Feed", "Remote", "https://x/2", "remotive", remote=True)],
    )
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200))) as client:
        jobs = collect("dummy.yaml", client)
    assert {job.id for job in jobs} == {"1", "2"}


def test_main_returns_non_zero_for_invalid_companies(tmp_path, capsys):
    cfg = tmp_path / "companies.yaml"
    cfg.write_text("companies: [bad]\n", encoding="utf-8")
    code = main(["check", "--companies", str(cfg)])
    out = capsys.readouterr().err
    assert code == 2
    assert "invalid companies.yaml" in out


def test_main_rejects_invalid_profile(tmp_path, capsys):
    profile = tmp_path / "profile.yaml"
    profile.write_text("remote: maybe\n", encoding="utf-8")
    code = main(["update", "--profile", str(profile), "--companies", "companies.yaml"])
    out = capsys.readouterr().err
    assert code == 2
    assert "remote" in out


def test_find_reports_request_failures(monkeypatch, capsys):
    def failing_fetch(slug, name, client):
        raise ValueError("boom")

    monkeypatch.setattr(cli, "CONNECTORS", {"lever": failing_fetch})
    code = main(["find", "Acme"])
    err = capsys.readouterr().err
    assert code == 0
    assert "source requests failed" in err
