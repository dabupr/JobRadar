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


def test_many_jobs_are_capped():
    jobs = [Job(str(i), "T" * 100, "Acme", "Barcelona", f"https://x/{i}", "lever") for i in range(500)]
    messages = format_messages(jobs)
    assert len(messages) == 10
    assert "more new jobs" in messages[-1]
    assert all(len(m) <= 1900 for m in messages)


def test_failed_post_does_not_leak_token(monkeypatch):
    import httpx
    import pytest

    from jobradar.notify import notify

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "SECRET123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "1")
    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(401)))
    job = Job("1", "Dev", "Acme", "Barcelona", "https://x/1", "lever")
    with pytest.raises(RuntimeError) as err:
        notify([job], client)
    assert "SECRET123" not in str(err.value) and "401" in str(err.value)
    assert err.value.__cause__ is None
