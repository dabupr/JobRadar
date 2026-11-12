import json

from jobradar.models import Job
from jobradar.site import write_site

JOBS = [
    Job("1", "A", "Acme", "Barcelona", "https://x/1", "lever", updated_at="2026-11-03"),
    Job("2", "B", "Acme", "Madrid", "https://x/2", "lever"),
    Job("3", "C", "Zeta", "Remote", "https://x/3", "ashby", remote=True),
]


def test_site_has_assets_and_compact_json(tmp_path, monkeypatch):
    monkeypatch.delenv("JOBRADAR_BASE_URL", raising=False)
    out = write_site(JOBS, tmp_path / "site")
    assert (out / "favicon.svg").exists() and (out / "og.png").stat().st_size > 1000
    assert (out / "robots.txt").read_text() == "User-agent: *\nAllow: /\n"
    assert not (out / "sitemap.xml").exists()
    raw = (out / "jobs.json").read_text(encoding="utf-8")
    assert ", " not in raw.split('"jobs"')[0]  # no spaces after separators
    job = json.loads(raw)["jobs"][0]
    assert "updated_at" not in job and job["posted"] == "2026-11-03"
    html = (out / "index.html").read_text(encoding="utf-8")
    assert "3 open jobs at 2 companies" in html
    assert 'content="og.png"' in html and "og:url" not in html


def test_site_with_base_url(tmp_path, monkeypatch):
    monkeypatch.setenv("JOBRADAR_BASE_URL", "https://example.github.io/JobRadar")
    out = write_site(JOBS, tmp_path / "site")
    html = (out / "index.html").read_text(encoding="utf-8")
    assert 'content="https://example.github.io/JobRadar/og.png"' in html
    assert '<meta property="og:url" content="https://example.github.io/JobRadar/">' in html
    assert '<link rel="canonical" href="https://example.github.io/JobRadar/">' in html
    assert "https://example.github.io/JobRadar/sitemap.xml" in (out / "robots.txt").read_text()
    assert "<loc>https://example.github.io/JobRadar/</loc>" in (out / "sitemap.xml").read_text()
