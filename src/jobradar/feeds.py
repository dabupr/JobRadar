"""Open job boards that list many companies at once (no per-company slug)."""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET

import httpx

from jobradar.http import get_with_retry
from jobradar.models import Job


def parse_remoteok(payload: list) -> list[Job]:
    jobs = []
    for idx, item in enumerate(payload, start=1):
        if not isinstance(item, dict) or "position" not in item:
            continue  # the first element is a legal notice
        required = ("id", "position", "url")
        missing = [field for field in required if not item.get(field)]
        if missing:
            print(f"warning: feed remoteok item {idx} missing {', '.join(missing)}", file=sys.stderr)
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
        required = ("id", "title", "url")
        missing = [field for field in required if not item.get(field)]
        if missing:
            print(f"warning: feed remotive item {idx} missing {', '.join(missing)}", file=sys.stderr)
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
        required = ("slug", "title", "url")
        missing = [field for field in required if not item.get(field)]
        if missing:
            print(f"warning: feed arbeitnow item {idx} missing {', '.join(missing)}", file=sys.stderr)
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


def fetch_remoteok(client: httpx.Client) -> list[Job]:
    resp = get_with_retry(client, "https://remoteok.com/api")
    return parse_remoteok(resp.json())


def fetch_remotive(client: httpx.Client) -> list[Job]:
    resp = get_with_retry(client, "https://remotive.com/api/remote-jobs")
    return parse_remotive(resp.json())


def fetch_arbeitnow(client: httpx.Client, pages: int = 5) -> list[Job]:
    jobs = []
    for page in range(1, pages + 1):
        resp = get_with_retry(client, "https://www.arbeitnow.com/api/job-board-api", params={"page": page})
        payload = resp.json()
        jobs.extend(parse_arbeitnow(payload))
        if not (payload.get("links") or {}).get("next"):
            break
    return jobs


def fetch_weworkremotely(client: httpx.Client) -> list[Job]:
    resp = get_with_retry(client, "https://weworkremotely.com/remote-jobs.rss")
    return parse_weworkremotely(resp.text)


FEEDS = {
    "remoteok": fetch_remoteok,
    "remotive": fetch_remotive,
    "arbeitnow": fetch_arbeitnow,
    "weworkremotely": fetch_weworkremotely,
}
