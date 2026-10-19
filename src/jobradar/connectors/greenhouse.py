from __future__ import annotations

import httpx

from jobradar.models import Job

API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"


def parse_greenhouse(slug: str, name: str, payload: dict) -> list[Job]:
    jobs = []
    for item in payload.get("jobs", []):
        location = (item.get("location") or {}).get("name", "")
        jobs.append(
            Job(
                id=f"greenhouse:{slug}:{item['id']}",
                title=item["title"],
                company=name,
                location=location,
                url=item["absolute_url"],
                source="greenhouse",
                remote="remote" in location.lower(),
                updated_at=item.get("updated_at"),
            )
        )
    return jobs


def fetch_greenhouse(slug: str, name: str, client: httpx.Client) -> list[Job]:
    resp = client.get(API.format(slug=slug))
    resp.raise_for_status()
    return parse_greenhouse(slug, name, resp.json())
