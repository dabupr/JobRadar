from __future__ import annotations

import httpx

from jobradar.models import Job

API = "https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true"


def parse_workable(slug: str, name: str, payload: dict) -> list[Job]:
    jobs = []
    for item in payload.get("jobs", []):
        location = ", ".join(p for p in (item.get("city"), item.get("country")) if p)
        jobs.append(
            Job(
                id=f"workable:{slug}:{item['shortcode']}",
                title=item["title"],
                company=name,
                location=location,
                url=item["url"],
                source="workable",
                remote=bool(item.get("telecommuting")),
                updated_at=item.get("published_on"),
            )
        )
    return jobs


def fetch_workable(slug: str, name: str, client: httpx.Client) -> list[Job]:
    resp = client.get(API.format(slug=slug))
    resp.raise_for_status()
    return parse_workable(slug, name, resp.json())
