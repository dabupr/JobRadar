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


def test_workable():
    from jobradar.connectors.workable import parse_workable

    payload = {"jobs": [{"shortcode": "AB12", "title": "QA", "url": "https://x/ab12",
                         "city": "Barcelona", "country": "Spain", "telecommuting": False}]}
    (job,) = parse_workable("acme", "Acme", payload)
    assert job.location == "Barcelona, Spain" and not job.remote


def test_recruitee_skips_unpublished():
    from jobradar.connectors.recruitee import parse_recruitee

    payload = {"offers": [
        {"id": 1, "title": "A", "careers_url": "https://x/1", "location": "Barcelona, Spain",
         "remote": True},
        {"id": 2, "title": "B", "careers_url": "https://x/2", "status": "draft"},
    ]}
    jobs = parse_recruitee("acme", "Acme", payload)
    assert [j.id for j in jobs] == ["recruitee:acme:1"] and jobs[0].remote


def test_personio():
    from jobradar.connectors.personio import parse_personio

    xml = ("<workzag-jobs><position><id>7</id><office>Barcelona</office>"
           "<name>Backend Engineer</name></position></workzag-jobs>")
    (job,) = parse_personio("acme", "Acme", xml)
    assert job.url == "https://acme.jobs.personio.de/job/7" and job.location == "Barcelona"


def test_smartrecruiters():
    from jobradar.connectors.smartrecruiters import parse_smartrecruiters

    payload = {"content": [{"id": "1", "name": "Dev", "location": {"city": "Barcelona",
                                                                   "country": "es", "remote": False}}]}
    (job,) = parse_smartrecruiters("Acme", "Acme", payload)
    assert job.location == "Barcelona, ES"
