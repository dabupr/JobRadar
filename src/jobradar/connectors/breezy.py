from __future__ import annotations

import httpx

from jobradar.models import Job

API = "https://{slug}.breezy.hr/json"


def parse_breezy(slug: str, name: str, payload: list) -> list[Job]:
    jobs = []
    for item in payload:
        loc = item.get("location") or {}
        country = (loc.get("country") or {}).get("name")
        location = loc.get("name") or ", ".join(p for p in (loc.get("city"), country) if p)
        jobs.append(
            Job(
                id=f"breezy:{slug}:{item['id']}",
                title=item["name"],
                company=name,
                location=location,
                url=item["url"],
                source="breezy",
                remote=bool(loc.get("is_remote")) or "remote" in location.lower(),
                updated_at=item.get("published_date"),
            )
        )
    return jobs


def fetch_breezy(slug: str, name: str, client: httpx.Client) -> list[Job]:
    resp = client.get(API.format(slug=slug))
    resp.raise_for_status()
    return parse_breezy(slug, name, resp.json())
