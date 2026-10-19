from __future__ import annotations

import httpx

from jobradar.models import Job

API = "https://api.ashbyhq.com/posting-api/job-board/{slug}"


def parse_ashby(slug: str, name: str, payload: dict) -> list[Job]:
    jobs = []
    for item in payload.get("jobs", []):
        if not item.get("isListed", True):
            continue
        jobs.append(
            Job(
                id=f"ashby:{slug}:{item['id']}",
                title=item["title"],
                company=name,
                location=item.get("location") or "",
                url=item["jobUrl"],
                source="ashby",
                remote=bool(item.get("isRemote")),
                updated_at=item.get("publishedAt"),
            )
        )
    return jobs


def fetch_ashby(slug: str, name: str, client: httpx.Client) -> list[Job]:
    resp = client.get(API.format(slug=slug))
    resp.raise_for_status()
    return parse_ashby(slug, name, resp.json())
