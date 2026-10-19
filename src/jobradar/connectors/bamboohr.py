from __future__ import annotations

import httpx

from jobradar.models import Job

API = "https://{slug}.bamboohr.com/careers/list"


def parse_bamboohr(slug: str, name: str, payload: dict) -> list[Job]:
    jobs = []
    for item in payload.get("result", []):
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
    resp = client.get(API.format(slug=slug), headers={"Accept": "application/json"})
    resp.raise_for_status()
    return parse_bamboohr(slug, name, resp.json())
