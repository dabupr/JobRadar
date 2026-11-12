"""Workday career sites, used by many large companies.

The slug is ``<tenant>.<wdN>/<site>``, read from the career site URL:
https://hp.wd5.myworkdayjobs.com/en-US/ExternalCareerSite -> ``hp.wd5/ExternalCareerSite``.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone

import httpx

from jobradar.http import request_with_retry
from jobradar.models import Job

HOST = "https://{tenant}.{pod}.myworkdayjobs.com"
API = HOST + "/wday/cxs/{tenant}/{site}/jobs"
PAGE = 20  # Workday refuses bigger pages
MAX_JOBS = 600  # big employers list thousands of jobs; keep each run quick and polite
SLUG = re.compile(r"^(?P<tenant>[\w-]+)\.(?P<pod>wd\d+)/(?P<site>[\w-]+)$")
DAYS_AGO = re.compile(r"(\d+)\+?\s+days?\s+ago", re.IGNORECASE)


def split_slug(slug: str) -> tuple[str, str, str]:
    match = SLUG.match(slug)
    if not match:
        raise ValueError(f"workday slug must look like tenant.wd5/Site, got {slug!r}")
    return match["tenant"], match["pod"], match["site"]


def posted_date(text: str | None, today: date | None = None) -> str | None:
    """Turn Workday's "Posted 3 Days Ago" into an ISO date. "30+ days" stays a lower bound."""
    if not text:
        return None
    today = today or datetime.now(timezone.utc).date()
    lower = text.lower()
    if "today" in lower:
        return today.isoformat()
    if "yesterday" in lower:
        return (today - timedelta(days=1)).isoformat()
    match = DAYS_AGO.search(lower)
    if match:
        return (today - timedelta(days=int(match[1]))).isoformat()
    return None


def parse_workday(slug: str, name: str, payload: dict, today: date | None = None) -> list[Job]:
    tenant, pod, site = split_slug(slug)
    base = HOST.format(tenant=tenant, pod=pod) + f"/{site}"
    jobs = []
    for item in payload.get("jobPostings") or []:
        path = item.get("externalPath")
        if not path or not item.get("title"):
            continue
        location = item.get("locationsText") or ""
        remote = "remote" in location.lower() or "remote" in item.get("remoteType", "").lower()
        jobs.append(
            Job(
                id=f"workday:{tenant}:{path.rsplit('_', 1)[-1] if '_' in path else path}",
                title=item["title"],
                company=name,
                location=location,
                url=base + path,
                source="workday",
                remote=remote,
                updated_at=posted_date(item.get("postedOn"), today),
            )
        )
    return jobs


def fetch_workday(
    slug: str, name: str, client: httpx.Client, max_jobs: int = MAX_JOBS
) -> list[Job]:
    tenant, pod, site = split_slug(slug)
    url = API.format(tenant=tenant, pod=pod, site=site)
    jobs: list[Job] = []
    total = None
    offset = 0
    while offset < max_jobs:
        body = {"appliedFacets": {}, "limit": PAGE, "offset": offset, "searchText": ""}
        resp = request_with_retry(
            client, "POST", url, json=body, headers={"Accept": "application/json"}
        )
        payload = resp.json()
        if total is None:
            total = payload.get("total") or 0  # only the first page carries the real total
        page = parse_workday(slug, name, payload)
        jobs.extend(page)
        offset += PAGE
        if not payload.get("jobPostings") or offset >= total:
            break
    return jobs
