import json

from jobradar.models import Job
from jobradar.site import write_site


def test_write_site(tmp_path):
    jobs = [
        Job("2", "B", "Zeta", "Madrid", "https://x/2", "lever"),
        Job("1", "A", "Acme", "Barcelona", "https://x/1", "lever", remote=True),
    ]
    write_site(jobs, tmp_path / "site")
    data = json.loads((tmp_path / "site" / "jobs.json").read_text(encoding="utf-8"))
    assert [j["id"] for j in data["jobs"]] == ["1", "2"]
    assert data["jobs"][0]["remote"] is True and "generated_at" in data
    assert "<title>JobRadar</title>" in (tmp_path / "site" / "index.html").read_text(encoding="utf-8")
