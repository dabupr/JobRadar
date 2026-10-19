from jobradar.connectors.ashby import parse_ashby
from jobradar.connectors.greenhouse import parse_greenhouse
from jobradar.connectors.lever import parse_lever


def test_greenhouse():
    payload = {"jobs": [{"id": 1, "title": "Python Dev", "absolute_url": "https://x/1",
                         "location": {"name": "Remote - Spain"}, "updated_at": "2026-01-01"}]}
    (job,) = parse_greenhouse("acme", "Acme", payload)
    assert job.id == "greenhouse:acme:1" and job.remote and job.company == "Acme"


def test_lever():
    payload = [{"id": "a", "text": "Data Engineer", "hostedUrl": "https://x/a",
                "categories": {"location": "Barcelona"}, "workplaceType": "hybrid",
                "createdAt": 1700000000000}]
    (job,) = parse_lever("acme", "Acme", payload)
    assert job.location == "Barcelona" and not job.remote


def test_ashby_skips_unlisted():
    payload = {"jobs": [
        {"id": "1", "title": "A", "jobUrl": "https://x/1", "isRemote": True},
        {"id": "2", "title": "B", "jobUrl": "https://x/2", "isListed": False},
    ]}
    jobs = parse_ashby("acme", "Acme", payload)
    assert [j.id for j in jobs] == ["ashby:acme:1"] and jobs[0].remote
