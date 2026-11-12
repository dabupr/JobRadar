from __future__ import annotations

import json
import os
import shutil
from dataclasses import asdict
from datetime import datetime, timezone
from html import escape
from importlib import resources
from pathlib import Path

from jobradar.dates import to_date
from jobradar.models import Job
from jobradar.places import CITY_ALIASES, SPAIN_WORDS, fold
from jobradar.seniority import LEVELS

ASSETS = ("favicon.svg", "og.png")


def job_record(job: Job) -> dict:
    """One job as the web page reads it: the raw ATS date is replaced by a plain posted date."""
    record = asdict(job)
    record.pop("updated_at")
    record["level"] = job.level
    record["posted"] = to_date(job.updated_at)
    return record


def render_index(html: str, jobs: list[Job], base_url: str | None) -> str:
    """Fill in the job count for previews, and absolute links when the public address is known."""
    companies = len({job.company for job in jobs})
    summary = (
        f"{len(jobs):,} open jobs at {companies:,} companies, straight from their career pages. "
        "Updated every day."
    )
    default = "Open jobs straight from company career pages, updated every day."
    html = html.replace(f'content="{default}"', f'content="{escape(summary)}"')
    if base_url:
        base = escape(base_url.rstrip("/") + "/")
        html = html.replace('content="og.png"', f'content="{base}og.png"')
        html = html.replace(
            '<meta property="og:type"',
            f'<link rel="canonical" href="{base}">\n<meta property="og:url" content="{base}">\n'
            '<meta property="og:type"',
        )
    return html


def write_site(jobs: list[Job], out: str | Path, base_url: str | None = None) -> Path:
    """Write the static job board: index.html next to a jobs.json with every job.

    `base_url` (or the JOBRADAR_BASE_URL variable) is the public address of the site, used for
    link previews and the sitemap.
    """
    base_url = base_url or os.environ.get("JOBRADAR_BASE_URL") or None
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload = {
        "generated_at": generated_at,
        "aliases": {k: [fold(n) for n in v] for k, v in CITY_ALIASES.items()},
        "spain_words": SPAIN_WORDS,
        "levels": LEVELS,
        "jobs": [job_record(job) for job in sorted(jobs, key=lambda j: (j.company, j.title))],
    }
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    (out / "jobs.json").write_text(text, encoding="utf-8")
    web = resources.files("jobradar.web")
    html = web.joinpath("index.html").read_text(encoding="utf-8")
    (out / "index.html").write_text(render_index(html, jobs, base_url), encoding="utf-8")
    for name in ASSETS:
        with resources.as_file(web.joinpath(name)) as src:
            shutil.copyfile(src, out / name)
    robots = "User-agent: *\nAllow: /\n"
    if base_url:
        base = base_url.rstrip("/") + "/"
        robots += f"Sitemap: {base}sitemap.xml\n"
        (out / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"<url><loc>{escape(base)}</loc><lastmod>{generated_at[:10]}</lastmod>"
            "<changefreq>daily</changefreq></url></urlset>\n",
            encoding="utf-8",
        )
    (out / "robots.txt").write_text(robots, encoding="utf-8")
    return out
