"""End-to-end tests of the CLI commands with fake connectors and no network."""

from __future__ import annotations

import json

import httpx
import pytest

from jobradar import cli
from jobradar.models import Job

BCN = Job(
    id="fake:acme:1",
    title="Senior Python Engineer",
    company="Acme",
    location="Barcelona, Spain",
    url="https://example.com/1",
    source="fake",
)
REMOTE = Job(
    id="fake:acme:2",
    title="Junior Data Analyst",
    company="Acme",
    location="Remote - Europe",
    url="https://example.com/2",
    source="fake",
    remote=True,
)
FEED_JOB = Job(
    id="feedx:9",
    title="Backend Developer",
    company="Feedco",
    location="Madrid",
    url="https://example.com/9",
    source="feedx",
)


def _http_error(status: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://example.com")
    return httpx.HTTPStatusError(
        "boom", request=request, response=httpx.Response(status, request=request)
    )


@pytest.fixture
def jobs_file(tmp_path, monkeypatch):
    """A companies.yaml with a working company, a broken one and a feed."""
    state = {"jobs": [BCN, REMOTE]}

    def fake(slug, name, client):
        return list(state["jobs"])

    def broken(slug, name, client):
        raise _http_error(404)

    monkeypatch.setitem(cli.CONNECTORS, "fake", fake)
    monkeypatch.setitem(cli.CONNECTORS, "broken", broken)
    monkeypatch.setitem(cli.FEEDS, "feedx", lambda client: [FEED_JOB])
    path = tmp_path / "companies.yaml"
    path.write_text(
        "companies:\n"
        "  - { name: Acme, ats: fake, slug: acme }\n"
        "  - { name: Gone, ats: broken, slug: gone }\n"
        "feeds: [feedx]\n",
        encoding="utf-8",
    )
    return path, state


def test_collect_skips_broken_sources(jobs_file, capsys):
    path, _ = jobs_file
    with httpx.Client() as client:
        jobs = cli.collect(str(path), client)
    assert [j.id for j in jobs] == [BCN.id, REMOTE.id, FEED_JOB.id]
    assert "warning: Gone" in capsys.readouterr().err


def test_invalid_companies_file_exits_with_an_error(tmp_path, capsys):
    path = tmp_path / "companies.yaml"
    path.write_text("companies:\n  - { name: Odd, ats: nope, slug: odd }\n", encoding="utf-8")
    assert cli.main(["search", "--companies", str(path)]) == 2
    assert "unknown value 'nope'" in capsys.readouterr().err


def test_collect_reports_failing_feed(tmp_path, monkeypatch, capsys):
    def down(client):
        raise _http_error(500)

    monkeypatch.setitem(cli.FEEDS, "down", down)
    path = tmp_path / "companies.yaml"
    path.write_text("feeds: [down]\n", encoding="utf-8")
    with httpx.Client() as client:
        assert cli.collect(str(path), client) == []
    assert "feed down" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["python"], [BCN.url]),
        (["--remote"], [REMOTE.url]),
        (["--city", "bcn"], [BCN.url]),
        (["--level", "junior"], [REMOTE.url]),
        (["developer"], [FEED_JOB.url]),
    ],
)
def test_search(jobs_file, capsys, argv, expected):
    path, _ = jobs_file
    assert cli.main(["search", *argv, "--companies", str(path)]) == 0
    out = capsys.readouterr().out
    assert [line.rsplit(" | ", 1)[1] for line in out.splitlines()] == expected


def test_check_counts_failures(jobs_file, capsys):
    path, _ = jobs_file
    assert cli.main(["check", "--companies", str(path)]) == 1
    captured = capsys.readouterr()
    assert "Acme [fake/acme]: ok (2 jobs)" in captured.out
    assert "Gone [broken/gone]: FAIL" in captured.out
    assert "feed feedx: ok (1 jobs)" in captured.out
    assert "2/3 sources ok" in captured.err


def test_check_unknown_sources_fail():
    assert cli.run_check([{"name": "Odd", "ats": "nope", "slug": "odd"}], ["missing"]) == 1


def test_check_feed_failure(monkeypatch, capsys):
    def down(client):
        raise _http_error(404)

    monkeypatch.setitem(cli.FEEDS, "down", down)
    assert cli.run_check([], ["down"]) == 1
    assert "feed down: FAIL" in capsys.readouterr().out


def test_export_writes_site(jobs_file, tmp_path, capsys):
    path, _ = jobs_file
    out = tmp_path / "site"
    assert cli.main(["export", "--companies", str(path), "--out", str(out)]) == 0
    assert (out / "index.html").exists()
    data = json.loads((out / "jobs.json").read_text(encoding="utf-8"))
    assert len(data["jobs"] if isinstance(data, dict) else data) == 3
    assert "wrote 3 jobs" in capsys.readouterr().err


def test_stats(jobs_file, capsys):
    path, _ = jobs_file
    assert cli.main(["stats", "--city", "barcelona", "--companies", str(path)]) == 0
    out = capsys.readouterr().out
    assert "total jobs: 3" in out
    assert "barcelona, with aliases: 1" in out
    assert "barcelona, with aliases + remote open to Spain/Europe: 2" in out
    assert "  Acme: 1" in out


def test_update_baseline_then_new_jobs(jobs_file, tmp_path, monkeypatch, capsys):
    path, state = jobs_file
    db = tmp_path / "seen.sqlite"
    profile = tmp_path / "profile.yaml"
    profile.write_text("keywords: [python, rust]\ncities: [barcelona]\n", encoding="utf-8")
    sent = []
    monkeypatch.setattr(cli, "notify", lambda jobs, client: sent.extend(jobs) or ["discord"])
    argv = ["update", "--companies", str(path), "--db", str(db), "--profile", str(profile)]

    assert cli.main([*argv, "--notify"]) == 0
    assert "first run" in capsys.readouterr().err
    assert sent == []

    rust = Job(
        id="fake:acme:3",
        title="Rust Engineer",
        company="Acme",
        location="Barcelona",
        url="https://example.com/3",
        source="fake",
    )
    java = Job(
        id="fake:acme:4",
        title="Java Engineer",
        company="Acme",
        location="Barcelona",
        url="https://example.com/4",
        source="fake",
    )
    state["jobs"] = [BCN, REMOTE, rust, java]
    assert cli.main([*argv, "--notify"]) == 0
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [f"NEW Acme | Rust Engineer | Barcelona | {rust.url}"]
    assert "1 new jobs" in captured.err and "notified: discord" in captured.err
    assert sent == [rust]

    assert cli.main(argv) == 0
    assert "0 new jobs" in capsys.readouterr().err


def test_find(monkeypatch, capsys):
    def only_acme(slug, name, client):
        if slug == "acmehq":
            return [BCN]
        if slug == "acme":
            return []  # an empty board is not a match
        raise _http_error(404)

    monkeypatch.setattr(cli, "CONNECTORS", {"fake": only_acme})
    assert cli.main(["find", "Acme", "Nobody Inc"]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "- { name: Acme, ats: fake, slug: acmehq }  # 1 jobs"
    assert "no match for 1 of 2: Nobody Inc" in captured.err
    assert "source requests failed" in captured.err


def test_slug_variants_add_a_capitalized_id_for_smartrecruiters():
    assert cli.slug_variants("Clarity AI") == [
        "clarityai",
        "clarity-ai",
        "clarityaiapp",
        "clarityaihq",
        "clarityaicareers",
        "Clarityai",
    ]
