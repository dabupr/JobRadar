from jobradar.models import Job
from jobradar.notify import format_messages


def test_messages_are_split_under_limit():
    jobs = [Job(str(i), "T" * 100, "Acme", "Barcelona", f"https://x/{i}", "lever") for i in range(40)]
    messages = format_messages(jobs)
    assert len(messages) > 1
    assert all(len(m) <= 1900 for m in messages)
    assert sum(m.count("https://") for m in messages) == 40


def test_no_jobs_no_messages():
    assert format_messages([]) == []
