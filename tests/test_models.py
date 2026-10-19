from jobradar.models import Job

JOB = Job("1", "Senior Python Developer", "Acme", "Madrid", "https://x", "lever", remote=False)


def test_matches_query_words():
    assert JOB.matches("python senior")
    assert not JOB.matches("rust")


def test_matches_remote_filter():
    assert not JOB.matches(remote=True)
