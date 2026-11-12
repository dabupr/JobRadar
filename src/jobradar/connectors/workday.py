"""Workday career sites, used by many large companies.

The slug is ``<tenant>.<wdN>/<site>``, read from the career site URL:
https://hp.wd5.myworkdayjobs.com/en-US/ExternalCareerSite -> ``hp.wd5/ExternalCareerSite``.
"""

from __future__ import annotations

import re
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone

import httpx

from jobradar.http import request_with_retry
from jobradar.models import Job

HOST = "https://{tenant}.{pod}.myworkdayjobs.com"
API = HOST + "/wday/cxs/{tenant}/{site}/jobs"
PAGE = 20  # Workday refuses bigger pages
MAX_JOBS = 600  # big employers list thousands of jobs; keep each run quick and polite
MAX_COUNTRY_JOBS = 1000  # every job in Spain, read with the country filter on top
FOCUS_COUNTRY = ("spain", "españa", "espana")
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


def find_country(facets: list, names: tuple[str, ...] = FOCUS_COUNTRY) -> tuple[str, str] | None:
    """Find the (facetParameter, id) that filters a Workday search to one country.

    Facets nest: a group such as ``locationMainGroup`` holds a ``locationCountry`` facet whose
    values carry a ``descriptor`` (the label) and an ``id``.
    """
    for facet in facets or []:
        param = facet.get("facetParameter", "")
        for value in facet.get("values") or []:
            if "values" in value:
                found = find_country([value], names)
                if found:
                    return found
            elif "country" in param.lower() and value.get("descriptor", "").lower() in names:
                return param, value["id"]
    return None


def _search(client: httpx.Client, url: str, facets: dict, offset: int) -> dict:
    body = {"appliedFacets": facets, "limit": PAGE, "offset": offset, "searchText": ""}
    resp = request_with_retry(
        client, "POST", url, json=body, headers={"Accept": "application/json"}
    )
    return resp.json()


def _pages(
    client: httpx.Client, url: str, slug: str, name: str, facets: dict, limit: int
) -> tuple[list[Job], dict]:
    """Read up to ``limit`` jobs of one search. Also return the first page (it has the facets)."""
    jobs: list[Job] = []
    first: dict = {}
    total = 0
    offset = 0
    while offset < limit:
        payload = _search(client, url, facets, offset)
        if offset == 0:
            first = payload
            total = payload.get("total") or 0  # only the first page carries the real total
        jobs.extend(parse_workday(slug, name, payload))
        offset += PAGE
        if not payload.get("jobPostings") or offset >= total:
            break
    return jobs, first


def fetch_workday(
    slug: str, name: str, client: httpx.Client, max_jobs: int = MAX_JOBS
) -> list[Job]:
    """The newest ``max_jobs`` jobs worldwide, plus every job in Spain (via the country filter)."""
    tenant, pod, site = split_slug(slug)
    url = API.format(tenant=tenant, pod=pod, site=site)
    jobs, first = _pages(client, url, slug, name, {}, max_jobs)
    if (first.get("total") or 0) <= len(jobs):
        return jobs  # already have everything
    country = find_country(first.get("facets") or [])
    if country is None:
        return jobs
    param, value = country
    local, _ = _pages(client, url, slug, name, {param: [value]}, MAX_COUNTRY_JOBS)
    seen = {job.id for job in jobs}
    for job in local:
        if job.id in seen:
            continue
        seen.add(job.id)
        if "spain" not in job.location.lower():
            # "3 Locations" or a bare city: say that one of them is in Spain
            job = replace(job, location=f"{job.location}, Spain" if job.location else "Spain")
        jobs.append(job)
    return jobs
