"""Open job boards that list many companies at once (no per-company slug)."""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET

import httpx

from jobradar.http import get_with_retry
from jobradar.models import Job
from jobradar.validate import has_fields


def parse_remoteok(payload: list) -> list[Job]:
    jobs = []
    for idx, item in enumerate(payload, start=1):
        if not isinstance(item, dict) or "position" not in item:
            continue  # the first element is a legal notice
        if not has_fields(item, ("id", "position", "url"), "feed remoteok", idx):
            continue
        jobs.append(
            Job(
                id=f"remoteok:{item['id']}",
                title=item["position"],
                company=item.get("company", ""),
                location=item.get("location") or "Remote",
                url=item.get("url", ""),
                source="remoteok",
                remote=True,
                updated_at=item.get("date"),
            )
        )
    return jobs


def parse_remotive(payload: dict) -> list[Job]:
    jobs = []
    for idx, item in enumerate(payload.get("jobs", []), start=1):
        if not has_fields(item, ("id", "title", "url"), "feed remotive", idx):
            continue
        jobs.append(
            Job(
                id=f"remotive:{item['id']}",
                title=item["title"],
                company=item.get("company_name", ""),
                location=item.get("candidate_required_location") or "Remote",
                url=item["url"],
                source="remotive",
                remote=True,
                updated_at=item.get("publication_date"),
            )
        )
    return jobs


def parse_arbeitnow(payload: dict) -> list[Job]:
    jobs = []
    for idx, item in enumerate(payload.get("data", []), start=1):
        if not has_fields(item, ("slug", "title", "url"), "feed arbeitnow", idx):
            continue
        jobs.append(
            Job(
                id=f"arbeitnow:{item['slug']}",
                title=item["title"],
                company=item.get("company_name", ""),
                location=item.get("location", ""),
                url=item["url"],
                source="arbeitnow",
                remote=bool(item.get("remote")),
                updated_at=str(item.get("created_at", "")) or None,
            )
        )
    return jobs


def parse_weworkremotely(xml_text: str) -> list[Job]:
    jobs = []
    for item in ET.fromstring(xml_text).iter("item"):
        full = item.findtext("title", "").strip()
        company, _, title = full.partition(":")
        if not title:
            company, title = "", full
        link = item.findtext("link", "").strip()
        jobs.append(
            Job(
                id=f"weworkremotely:{item.findtext('guid') or link}",
                title=title.strip(),
                company=company.strip(),
                location=item.findtext("region") or "Remote",
                url=link,
                source="weworkremotely",
                remote=True,
                updated_at=item.findtext("pubDate"),
            )
        )
    return jobs


def parse_himalayas(payload: dict) -> list[Job]:
    jobs = []
    for item in payload.get("jobs") or []:
        link = item.get("guid") if str(item.get("guid", "")).startswith("http") else None
        link = link or item.get("applicationLink")
        if not link or not item.get("title"):
            continue
        places = item.get("locationRestrictions") or []
        jobs.append(
            Job(
                id=f"himalayas:{item.get('guid') or link}",
                title=item["title"],
                company=item.get("companyName", ""),
                location=", ".join(places) or "Anywhere",
                url=link,
                source="himalayas",
                remote=True,
                updated_at=str(item["pubDate"]) if item.get("pubDate") else None,
            )
        )
    return jobs


def parse_jobicy(payload: dict) -> list[Job]:
    return [
        Job(
            id=f"jobicy:{item['id']}",
            title=html.unescape(item["jobTitle"]),
            company=html.unescape(item.get("companyName", "")),
            location=item.get("jobGeo") or "Anywhere",
            url=item["url"],
            source="jobicy",
            remote=True,
            updated_at=item.get("pubDate"),
        )
        for item in payload.get("jobs") or []
        if item.get("id") and item.get("jobTitle") and item.get("url")
    ]


TAG = re.compile(r"<[^>]+>")
URL = re.compile(r"https?://|www\.|\.(com|io|ai|dev|co)\b", re.IGNORECASE)
ROLE = re.compile(
    r"engineer|developer|scientist|designer|manager|lead|architect|analyst|devops|sre|"
    r"programmer|researcher|intern|founding|head of|director|product|marketing|sales|"
    r"recruiter|writer|specialist|consultant|administrator|technician|cto|vp",
    re.IGNORECASE,
)
NOT_PLACE = re.compile(
    r"full[- ]?time|part[- ]?time|contract|freelance|salary|equity|visa|\$|€|£|\d+\s*k\b|"
    r"series [a-e]|seed|funded|employees",
    re.IGNORECASE,
)


def _hn_header(text: str) -> str:
    first = re.split(r"<p>|\n", text or "", maxsplit=1)[0]
    return html.unescape(TAG.sub("", first)).strip()


def parse_hn_comment(item: dict) -> Job | None:
    """Read the usual "Company | Role | Place | Remote | ..." first line of a hiring comment."""
    header = _hn_header(item.get("text") or "")
    parts = [p.strip() for p in header.split("|") if p.strip()]
    if len(parts) < 2 or len(header) > 400:
        return None
    company, rest = parts[0], parts[1:]
    title = next((p for p in rest if ROLE.search(p) and not URL.search(p)), None)
    if title is None:
        return None
    places = [
        p for p in rest
        if p is not title and not URL.search(p) and not NOT_PLACE.search(p) and len(p) <= 80
    ]
    remote = "remote" in header.lower()
    return Job(
        id=f"hn:{item['id']}",
        title=title,
        company=company,
        location=" / ".join(places) or ("Remote" if remote else ""),
        url=f"https://news.ycombinator.com/item?id={item['id']}",
        source="hackernews",
        remote=remote,
        updated_at=str(item["created_at_i"]) if item.get("created_at_i") else item.get("created_at"),
    )


def parse_hn_thread(payload: dict) -> list[Job]:
    jobs = []
    for child in payload.get("children") or []:
        if child.get("id") and child.get("text"):
            job = parse_hn_comment(child)
            if job:
                jobs.append(job)
    return jobs


def fetch_remoteok(client: httpx.Client) -> list[Job]:
    resp = get_with_retry(client, "https://remoteok.com/api")
    return parse_remoteok(resp.json())


def fetch_remotive(client: httpx.Client) -> list[Job]:
    resp = get_with_retry(client, "https://remotive.com/api/remote-jobs")
    return parse_remotive(resp.json())


def fetch_arbeitnow(client: httpx.Client, pages: int = 5) -> list[Job]:
    jobs = []
    for page in range(1, pages + 1):
        resp = get_with_retry(
            client, "https://www.arbeitnow.com/api/job-board-api", params={"page": page}
        )
        payload = resp.json()
        jobs.extend(parse_arbeitnow(payload))
        if not (payload.get("links") or {}).get("next"):
            break
    return jobs


def fetch_weworkremotely(client: httpx.Client) -> list[Job]:
    resp = get_with_retry(client, "https://weworkremotely.com/remote-jobs.rss")
    return parse_weworkremotely(resp.text)


def fetch_himalayas(client: httpx.Client, max_jobs: int = 500) -> list[Job]:
    jobs: list[Job] = []
    offset = 0
    while offset < max_jobs:
        resp = get_with_retry(
            client, "https://himalayas.app/jobs/api", params={"limit": 20, "offset": offset}
        )
        payload = resp.json()
        jobs.extend(parse_himalayas(payload))
        offset += 20
        if not payload.get("jobs") or offset >= (payload.get("totalCount") or 0):
            break
    return jobs


def fetch_jobicy(client: httpx.Client) -> list[Job]:
    resp = get_with_retry(client, "https://jobicy.com/api/v2/remote-jobs", params={"count": 100})
    return parse_jobicy(resp.json())


HN_API = "https://hn.algolia.com/api/v1"


def fetch_hackernews(client: httpx.Client) -> list[Job]:
    """Jobs from the latest monthly "Ask HN: Who is hiring?" thread."""
    resp = get_with_retry(
        client,
        f"{HN_API}/search_by_date",
        params={"tags": "story,author_whoishiring", "hitsPerPage": 10},
    )
    story = next(
        (h for h in resp.json().get("hits", []) if "who is hiring" in h.get("title", "").lower()),
        None,
    )
    if story is None:
        return []
    resp = get_with_retry(client, f"{HN_API}/items/{story['objectID']}")
    return parse_hn_thread(resp.json())


FEEDS = {
    "remoteok": fetch_remoteok,
    "remotive": fetch_remotive,
    "arbeitnow": fetch_arbeitnow,
    "weworkremotely": fetch_weworkremotely,
    "himalayas": fetch_himalayas,
    "jobicy": fetch_jobicy,
    "hackernews": fetch_hackernews,
}
