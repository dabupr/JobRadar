from jobradar.connectors.bamboohr import parse_bamboohr
from jobradar.connectors.breezy import parse_breezy
from jobradar.connectors.teamtailor import parse_teamtailor
from jobradar.feeds import (
    parse_arbeitnow,
    parse_remoteok,
    parse_remotive,
    parse_weworkremotely,
)

TEAMTAILOR = """<?xml version="1.0"?>
<rss version="2.0" xmlns:tt="https://teamtailor.com/locations"><channel>
<item><title>Backend Engineer</title><link>https://acme.teamtailor.com/jobs/1-backend</link>
<guid>1</guid><pubDate>Mon, 05 Jan 2026 10:00:00 +0000</pubDate><remoteStatus>hybrid</remoteStatus>
<tt:locations><tt:location><tt:city>Barcelona</tt:city><tt:country>Spain</tt:country>
</tt:location></tt:locations></item>
<item><title>Designer</title><link>https://acme.teamtailor.com/jobs/2</link><guid>2</guid>
<remoteStatus>fully</remoteStatus></item>
</channel></rss>"""

WWR = """<rss><channel>
<item><title>Acme: Senior Python Developer</title><region>Anywhere in the World</region>
<link>https://weworkremotely.com/jobs/1</link><guid>g1</guid></item>
</channel></rss>"""


def test_teamtailor():
    one, two = parse_teamtailor("acme", "Acme", TEAMTAILOR)
    assert one.location == "Barcelona, Spain" and not one.remote and one.id == "teamtailor:acme:1"
    assert two.remote


def test_bamboohr():
    payload = {"result": [{"id": "5", "jobOpeningName": "QA", "location": {"city": "Madrid"},
                           "isRemote": None}]}
    (job,) = parse_bamboohr("acme", "Acme", payload)
    assert job.url == "https://acme.bamboohr.com/careers/5" and job.location == "Madrid"


def test_breezy():
    payload = [{"id": "x", "name": "Data Analyst", "url": "https://acme.breezy.hr/p/x",
                "location": {"name": "Barcelona, Spain", "is_remote": False}}]
    (job,) = parse_breezy("acme", "Acme", payload)
    assert job.location == "Barcelona, Spain" and not job.remote


def test_remoteok_skips_legal_notice():
    payload = [{"legal": "notice"}, {"id": "1", "position": "Go Dev", "company": "Acme",
                                      "url": "https://remoteok.com/1"}]
    (job,) = parse_remoteok(payload)
    assert job.remote and job.company == "Acme"


def test_remotive():
    payload = {"jobs": [{"id": 1, "title": "SRE", "company_name": "Acme", "url": "https://x",
                         "candidate_required_location": "Europe"}]}
    (job,) = parse_remotive(payload)
    assert job.location == "Europe" and job.source == "remotive"


def test_arbeitnow():
    payload = {"data": [{"slug": "a-b", "title": "Dev", "company_name": "Acme",
                         "url": "https://x", "location": "Berlin", "remote": False}]}
    (job,) = parse_arbeitnow(payload)
    assert job.id == "arbeitnow:a-b" and not job.remote


def test_weworkremotely_splits_company():
    (job,) = parse_weworkremotely(WWR)
    assert job.company == "Acme" and job.title == "Senior Python Developer"
