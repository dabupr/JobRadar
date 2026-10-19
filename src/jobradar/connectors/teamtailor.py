from __future__ import annotations

import xml.etree.ElementTree as ET

import httpx

from jobradar.models import Job

API = "https://{slug}.teamtailor.com/jobs.rss"


def _text(item: ET.Element, *names: str) -> str:
    """Text of the first child whose local name (namespace ignored) is one of names."""
    for child in item.iter():
        if child.tag.rsplit("}", 1)[-1] in names and child.text and child.text.strip():
            return child.text.strip()
    return ""


def parse_teamtailor(slug: str, name: str, xml_text: str) -> list[Job]:
    jobs = []
    for item in ET.fromstring(xml_text).iter("item"):
        link = item.findtext("link", "").strip()
        city = _text(item, "city")
        country = _text(item, "country")
        remote_status = _text(item, "remoteStatus").lower()
        location = ", ".join(p for p in (city, country) if p)
        jobs.append(
            Job(
                id=f"teamtailor:{slug}:{item.findtext('guid') or link}",
                title=item.findtext("title", "").strip(),
                company=name,
                location=location,
                url=link,
                source="teamtailor",
                remote=remote_status in ("fully", "remote") or "remote" in location.lower(),
                updated_at=item.findtext("pubDate"),
            )
        )
    return jobs


def fetch_teamtailor(slug: str, name: str, client: httpx.Client) -> list[Job]:
    resp = client.get(API.format(slug=slug))
    resp.raise_for_status()
    return parse_teamtailor(slug, name, resp.text)
