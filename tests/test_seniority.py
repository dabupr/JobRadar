import pytest

from jobradar.models import Job
from jobradar.profile import Profile
from jobradar.seniority import level_of


@pytest.mark.parametrize(
    "title, expected",
    [
        ("Software Engineering Intern", "intern"),
        ("Becari de Dades (Pràctiques)", "intern"),
        ("Working Student Marketing", "intern"),
        ("Junior Data Engineer", "junior"),
        ("Graduate Software Engineer", "junior"),
        ("Data Engineer", "mid"),
        ("Sènior Backend Engineer", "senior"),
        ("Sr. Data Engineer", "senior"),
        ("Staff Engineer", "lead"),
        ("Tech Lead, Payments", "lead"),
        ("Principal Product Designer", "lead"),
        ("Senior Engineering Manager", "manager"),
        ("Head of Data", "manager"),
        ("Responsable de Producto", "manager"),
        ("Director de Ingeniería", "manager"),
        ("Lead Generation Specialist", "mid"),
    ],
)
def test_level_of(title, expected):
    assert level_of(title) == expected


def test_job_matches_levels():
    job = Job("1", "Senior Python Developer", "Acme", "Barcelona", "https://x", "lever")
    assert job.matches(levels=["senior", "lead"])
    assert not job.matches(levels=["junior"])
    assert job.matches(levels=[])


def test_profile_levels():
    job = Job("1", "Junior Python Developer", "Acme", "Barcelona", "https://x", "lever")
    assert Profile(levels=["junior"]).accepts(job)
    assert not Profile(levels=["senior"]).accepts(job)
