from __future__ import annotations

import sys

import httpx

from jobradar.http import get_with_retry
from jobradar.models import Job

API = "https://api.smartrecruiters.com/v1/companies/{slug}/postings"
PAGE = 100


def parse_smartrecruiters(slug: str, name: str, payload: dict) -> list[Job]:
    jobs = []
    for idx, item in enumerate(payload.get("content", []), start=1):
        required = ("id", "name")
        missing = [field for field in required if not item.get(field)]
        if missing:
            print(
                f"warning: smartrecruiters/{slug} ({name}) item {idx} missing {', '.join(missing)}",
                file=sys.stderr,
            )
            continue
        loc = item.get("location") or {}
        location = ", ".join(p for p in (loc.get("city"), loc.get("country", "").upper()) if p)
        jobs.append(
            Job(
                id=f"smartrecruiters:{slug}:{item['id']}",
                title=item["name"],
                company=name,
                location=location,
                url=f"https://jobs.smartrecruiters.com/{slug}/{item['id']}",
                source="smartrecruiters",
                remote=bool(loc.get("remote")),
                updated_at=item.get("releasedDate"),
            )
        )
    return jobs


def fetch_smartrecruiters(slug: str, name: str, client: httpx.Client) -> list[Job]:
    jobs: list[Job] = []
    offset = 0
    while True:
        resp = get_with_retry(client, API.format(slug=slug), params={"limit": PAGE, "offset": offset})
        payload = resp.json()
        jobs.extend(parse_smartrecruiters(slug, name, payload))
        offset += PAGE
        if offset >= payload.get("totalFound", 0):
            return jobs
