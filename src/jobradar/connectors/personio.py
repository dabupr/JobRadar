from __future__ import annotations

import xml.etree.ElementTree as ET

import httpx

from jobradar.http import get_with_retry
from jobradar.models import Job

API = "https://{slug}.jobs.personio.de/xml"


def parse_personio(slug: str, name: str, xml_text: str) -> list[Job]:
    jobs = []
    for pos in ET.fromstring(xml_text).iter("position"):
        job_id = pos.findtext("id", "")
        office = pos.findtext("office", "")
        jobs.append(
            Job(
                id=f"personio:{slug}:{job_id}",
                title=pos.findtext("name", ""),
                company=name,
                location=office,
                url=f"https://{slug}.jobs.personio.de/job/{job_id}",
                source="personio",
                remote="remote" in office.lower(),
                updated_at=pos.findtext("createdAt"),
            )
        )
    return jobs


def fetch_personio(slug: str, name: str, client: httpx.Client) -> list[Job]:
    resp = get_with_retry(client, API.format(slug=slug))
    return parse_personio(slug, name, resp.text)
