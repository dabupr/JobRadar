from __future__ import annotations

import sys

import httpx

from jobradar.http import get_with_retry
from jobradar.models import Job

API = "https://api.ashbyhq.com/posting-api/job-board/{slug}"


def parse_ashby(slug: str, name: str, payload: dict) -> list[Job]:
    jobs = []
    for idx, item in enumerate(payload.get("jobs", []), start=1):
        if not item.get("isListed", True):
            continue
        required = ("id", "title", "jobUrl")
        missing = [field for field in required if not item.get(field)]
        if missing:
            print(
                f"warning: ashby/{slug} ({name}) item {idx} missing {', '.join(missing)}",
                file=sys.stderr,
            )
            continue
        jobs.append(
            Job(
                id=f"ashby:{slug}:{item['id']}",
                title=item["title"],
                company=name,
                location=item.get("location") or "",
                url=item["jobUrl"],
                source="ashby",
                remote=bool(item.get("isRemote")),
                updated_at=item.get("publishedAt"),
            )
        )
    return jobs

def fetch_ashby(slug: str, name: str, client: httpx.Client) -> list[Job]:
def fetch_ashby(slug: str, name: str, client: httpx.Client) -> list[Job]:
    resp = get_with_retry(client, API.format(slug=slug))
    return parse_ashby(slug, name, resp.json())
