from __future__ import annotations

import httpx

from jobradar.http import get_with_retry
from jobradar.models import Job
from jobradar.validate import has_fields

API = "https://api.lever.co/v0/postings/{slug}?mode=json"


def parse_lever(slug: str, name: str, payload: list[dict]) -> list[Job]:
    jobs = []
    for idx, item in enumerate(payload, start=1):
        if not has_fields(item, ("id", "text", "hostedUrl"), f"lever/{slug} ({name})", idx):
            continue
        categories = item.get("categories") or {}
        location = categories.get("location") or ""
        workplace = item.get("workplaceType", "")
        jobs.append(
            Job(
                id=f"lever:{slug}:{item['id']}",
                title=item["text"],
                company=name,
                location=location,
                url=item["hostedUrl"],
                source="lever",
                remote=workplace == "remote" or "remote" in location.lower(),
                updated_at=str(item["createdAt"]) if item.get("createdAt") else None,
            )
        )
    return jobs

def fetch_lever(slug: str, name: str, client: httpx.Client) -> list[Job]:
    resp = get_with_retry(client, API.format(slug=slug))
    return parse_lever(slug, name, resp.json())
