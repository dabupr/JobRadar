from jobradar.models import Job
from jobradar.profile import Profile
from jobradar.storage import Store


def job(i, title="Python Dev", location="Barcelona", remote=False):
    return Job(str(i), title, "Acme", location, f"https://x/{i}", "lever", remote=remote)


def test_upsert_returns_only_new_jobs():
    store = Store(":memory:")
    assert store.is_empty()
    assert [j.id for j in store.upsert([job(1), job(2)])] == ["1", "2"]
    assert not store.is_empty()
    assert [j.id for j in store.upsert([job(2), job(3)])] == ["3"]


def test_upsert_ignores_duplicates_in_one_run():
    store = Store(":memory:")
    assert len(store.upsert([job(1), job(1)])) == 1


def test_profile_keywords_and_exclude():
    profile = Profile(keywords=["python"], exclude=["intern"])
    assert profile.accepts(job(1))
    assert not profile.accepts(job(2, title="Python Intern"))
    assert not profile.accepts(job(3, title="Java Dev"))


def test_profile_city_and_remote():
    profile = Profile(cities=["barcelona"], remote=True)
    assert profile.accepts(job(1))
    assert not profile.accepts(job(2, location="Madrid"))
    assert profile.accepts(job(3, location="Madrid", remote=True))
    assert not Profile(cities=["barcelona"]).accepts(job(4, location="Madrid", remote=True))
