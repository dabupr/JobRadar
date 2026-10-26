from __future__ import annotations

import sys

import httpx

from jobradar.http import get_with_retry
from jobradar.models import Job

API = "https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true"


def parse_workable(slug: str, name: str, payload: dict) -> list[Job]:
    jobs = []
    for idx, item in enumerate(payload.get("jobs", []), start=1):
        required = ("shortcode", "title", "url")
        missing = [field for field in required if not item.get(field)]
        if missing:
            print(
                f"warning: workable/{slug} ({name}) item {idx} missing {', '.join(missing)}",
                file=sys.stderr,
            )
            continue
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
    resp = get_with_retry(client, API.format(slug=slug))
    return parse_workable(slug, name, resp.json())
