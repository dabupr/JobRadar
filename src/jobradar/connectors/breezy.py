from __future__ import annotations

import sys

import httpx

from jobradar.http import get_with_retry
from jobradar.models import Job

API = "https://{slug}.breezy.hr/json"


def parse_breezy(slug: str, name: str, payload: list) -> list[Job]:
    jobs = []
    for idx, item in enumerate(payload, start=1):
        required = ("id", "name", "url")
        missing = [field for field in required if not item.get(field)]
        if missing:
            print(
                f"warning: breezy/{slug} ({name}) item {idx} missing {', '.join(missing)}",
                file=sys.stderr,
            )
            continue
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
    resp = get_with_retry(client, API.format(slug=slug))
    return parse_breezy(slug, name, resp.json())
