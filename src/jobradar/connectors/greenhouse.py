from __future__ import annotations

import sys

import httpx

from jobradar.http import get_with_retry
from jobradar.models import Job

API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"


def parse_greenhouse(slug: str, name: str, payload: dict) -> list[Job]:
    jobs = []
    for idx, item in enumerate(payload.get("jobs", []), start=1):
        required = ("id", "title", "absolute_url")
        missing = [field for field in required if not item.get(field)]
        if missing:
            print(
                f"warning: greenhouse/{slug} ({name}) item {idx} missing {', '.join(missing)}",
                file=sys.stderr,
            )
            continue
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
    resp = get_with_retry(client, API.format(slug=slug))
    return parse_greenhouse(slug, name, resp.json())
