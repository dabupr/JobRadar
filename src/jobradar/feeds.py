"""Open job boards that list many companies at once (no per-company slug)."""
from __future__ import annotations

import xml.etree.ElementTree as ET

import httpx

from jobradar.models import Job


def parse_remoteok(payload: list) -> list[Job]:
    jobs = []
    for item in payload:
        if not isinstance(item, dict) or "position" not in item:
            continue  # the first element is a legal notice
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
    return [
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
        for item in payload.get("jobs", [])
    ]


def parse_arbeitnow(payload: dict) -> list[Job]:
    return [
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
        for item in payload.get("data", [])
    ]


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
    resp = client.get("https://remoteok.com/api")
    resp.raise_for_status()
    return parse_remoteok(resp.json())


def fetch_remotive(client: httpx.Client) -> list[Job]:
    resp = client.get("https://remotive.com/api/remote-jobs")
    resp.raise_for_status()
    return parse_remotive(resp.json())


def fetch_arbeitnow(client: httpx.Client, pages: int = 5) -> list[Job]:
    jobs = []
    for page in range(1, pages + 1):
        resp = client.get("https://www.arbeitnow.com/api/job-board-api", params={"page": page})
        resp.raise_for_status()
        payload = resp.json()
        jobs.extend(parse_arbeitnow(payload))
        if not (payload.get("links") or {}).get("next"):
            break
    return jobs


def fetch_weworkremotely(client: httpx.Client) -> list[Job]:
    resp = client.get("https://weworkremotely.com/remote-jobs.rss")
    resp.raise_for_status()
    return parse_weworkremotely(resp.text)


FEEDS = {
    "remoteok": fetch_remoteok,
    "remotive": fetch_remotive,
    "arbeitnow": fetch_arbeitnow,
    "weworkremotely": fetch_weworkremotely,
}
