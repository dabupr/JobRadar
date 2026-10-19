from __future__ import annotations

import httpx

from jobradar.models import Job

API = "https://{slug}.recruitee.com/api/offers/"


def parse_recruitee(slug: str, name: str, payload: dict) -> list[Job]:
    jobs = []
    for item in payload.get("offers", []):
        if item.get("status", "published") != "published":
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
    resp = client.get(API.format(slug=slug))
    resp.raise_for_status()
    return parse_recruitee(slug, name, resp.json())
