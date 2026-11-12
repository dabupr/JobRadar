from datetime import date

import httpx
import pytest

from jobradar.connectors import CONNECTORS
from jobradar.connectors.workday import fetch_workday, parse_workday, posted_date, split_slug
from jobradar.feeds import FEEDS, parse_himalayas, parse_hn_comment, parse_hn_thread, parse_jobicy

TODAY = date(2026, 11, 12)


def test_workday_slug():
    assert split_slug("hp.wd5/ExternalCareerSite") == ("hp", "wd5", "ExternalCareerSite")
    with pytest.raises(ValueError):
        split_slug("hp")
    assert CONNECTORS["workday"] is fetch_workday


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Posted Today", "2026-11-12"),
        ("Posted Yesterday", "2026-11-11"),
        ("Posted 3 Days Ago", "2026-11-09"),
        ("Posted 30+ Days Ago", "2026-10-13"),
        ("", None),
        (None, None),
    ],
)
def test_workday_posted_date(text, expected):
    assert posted_date(text, TODAY) == expected


def test_parse_workday():
    payload = {
        "total": 2,
        "jobPostings": [
            {
                "title": "Software Engineering Intern",
                "externalPath": "/job/Sant-Cugat-del-Valles-Barcelona-Spain/"
                "Software-Engineering-Intern_UNI4787-1",
                "locationsText": "Sant Cugat del Valles, Barcelona, Spain",
                "postedOn": "Posted 2 Days Ago",
            },
            {"title": "No path"},
        ],
    }
    (job,) = parse_workday("hp.wd5/ExternalCareerSite", "HP", payload, TODAY)
    assert job.id == "workday:hp:UNI4787-1"
    assert job.url.startswith("https://hp.wd5.myworkdayjobs.com/ExternalCareerSite/job/")
    assert job.updated_at == "2026-11-10" and job.matches(city="barcelona") and not job.remote


def test_fetch_workday_pages_and_stops():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = request.read()
        calls.append(body)
        offset = len(calls) - 1
        postings = [
            {"title": f"Job {offset}-{i}", "externalPath": f"/job/x/J_{offset}{i}"}
            for i in range(20)
        ]
        # Workday only reports the real total on the first page
        return httpx.Response(
            200, json={"total": 45 if offset == 0 else 0, "jobPostings": postings}
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    jobs = fetch_workday("acme.wd1/Careers", "Acme", client)
    assert len(calls) == 3 and len(jobs) == 60
    assert all(b'"limit":20' in body.replace(b" ", b"") for body in calls)
    calls.clear()
    assert len(fetch_workday("acme.wd1/Careers", "Acme", client, max_jobs=20)) == 20


def test_himalayas():
    payload = {
        "jobs": [
            {
                "title": "Backend Engineer",
                "companyName": "Acme",
                "locationRestrictions": ["Spain", "Portugal"],
                "pubDate": 1793701230,
                "applicationLink": "https://acme.com/apply",
                "guid": "https://himalayas.app/companies/acme/jobs/backend-engineer",
            },
            {"title": "No link"},
        ]
    }
    (job,) = parse_himalayas(payload)
    assert job.url.startswith("https://himalayas.app/") and job.remote
    assert job.location == "Spain, Portugal" and job.updated_at == "1793701230"


def test_jobicy():
    payload = {
        "jobs": [
            {
                "id": 7,
                "url": "https://jobicy.com/jobs/7-dev",
                "jobTitle": "Dev &amp; Ops",
                "companyName": "Acme",
                "jobGeo": "Europe",
                "pubDate": "2026-11-10T12:00:00+00:00",
            }
        ]
    }
    (job,) = parse_jobicy(payload)
    assert job.title == "Dev & Ops" and job.location == "Europe" and job.id == "jobicy:7"


def test_hn_comment():
    item = {
        "id": 42,
        "created_at_i": 1793701230,
        "text": "Acme Corp | Senior Backend Engineer | Barcelona, Spain | Hybrid | Full-time |"
        " https:&#x2F;&#x2F;acme.com<p>We build things.",
    }
    job = parse_hn_comment(item)
    assert job.company == "Acme Corp" and job.title == "Senior Backend Engineer"
    assert job.location == "Barcelona, Spain / Hybrid" and not job.remote
    assert job.url == "https://news.ycombinator.com/item?id=42" and job.matches(city="barcelona")


def test_hn_thread_skips_chatter():
    payload = {
        "children": [
            {"id": 1, "text": "Is anyone hiring juniors?"},
            {"id": 2, "text": "Acme | Data Scientist | REMOTE (EU)"},
            {"id": 3, "text": None},
            {"id": 4, "text": "Beta | $150k | equity"},
        ]
    }
    (job,) = parse_hn_thread(payload)
    assert job.id == "hn:2" and job.remote and job.location == "REMOTE (EU)"


def test_new_feeds_registered():
    assert {"himalayas", "jobicy", "hackernews"} <= set(FEEDS)
