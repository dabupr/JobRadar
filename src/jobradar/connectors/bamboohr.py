from __future__ import annotations

import httpx

from jobradar.http import get_with_retry
from jobradar.models import Job
from jobradar.validate import has_fields

API = "https://{slug}.bamboohr.com/careers/list"


def parse_bamboohr(slug: str, name: str, payload: dict) -> list[Job]:
    jobs = []
    for idx, item in enumerate(payload.get("result", []), start=1):
        if not has_fields(item, ("id", "jobOpeningName"), f"bamboohr/{slug} ({name})", idx):
            continue
        loc = item.get("location") or {}
        location = ", ".join(p for p in (loc.get("city"), loc.get("state")) if p)
        remote = bool(item.get("isRemote")) or "remote" in (
            f"{location} {item.get('locationType', '')}".lower()
        )
        jobs.append(
            Job(
                id=f"bamboohr:{slug}:{item['id']}",
                title=item["jobOpeningName"],
                company=name,
                location=location,
                url=f"https://{slug}.bamboohr.com/careers/{item['id']}",
                source="bamboohr",
                remote=remote,
            )
        )
    return jobs

def fetch_bamboohr(slug: str, name: str, client: httpx.Client) -> list[Job]:
    resp = get_with_retry(client, API.format(slug=slug), headers={"Accept": "application/json"})
    return parse_bamboohr(slug, name, resp.json())
