from __future__ import annotations

import httpx

from jobradar.http import get_with_retry
from jobradar.models import Job
from jobradar.validate import has_fields

API = "https://{slug}.recruitee.com/api/offers/"


def parse_recruitee(slug: str, name: str, payload: dict) -> list[Job]:
    jobs = []
    for idx, item in enumerate(payload.get("offers", []), start=1):
        if item.get("status", "published") != "published":
            continue
        if not has_fields(item, ("id", "title", "careers_url"), f"recruitee/{slug} ({name})", idx):
            continue
        location = item.get("location") or ", ".join(
            p for p in (item.get("city"), item.get("country")) if p
        )
        jobs.append(
            Job(
                id=f"recruitee:{slug}:{item['id']}",
                title=item["title"],
                company=name,
                location=location,
                url=item["careers_url"],
                source="recruitee",
                remote=bool(item.get("remote")),
                updated_at=item.get("published_at"),
            )
        )
    return jobs

def fetch_recruitee(slug: str, name: str, client: httpx.Client) -> list[Job]:
    resp = get_with_retry(client, API.format(slug=slug))
    return parse_recruitee(slug, name, resp.json())
