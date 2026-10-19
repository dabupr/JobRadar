from __future__ import annotations

import os

import httpx

from jobradar.models import Job

LIMIT = 1800
MAX_MESSAGES = 10  # a big first import must not hit Discord/Telegram rate limits


def format_messages(jobs: list[Job]) -> list[str]:
    """One line per job, split into messages small enough for Discord and Telegram."""
    messages, current = [], ""
    for job in jobs:
        line = f"{job.company}: {job.title} ({job.location or 'n/a'}) {job.url}\n"
        if current and len(current) + len(line) > LIMIT:
            messages.append(current.strip())
            current = ""
        current += line
    if current:
        messages.append(current.strip())
    if len(messages) > MAX_MESSAGES:
        hidden = sum(m.count("\n") + 1 for m in messages[MAX_MESSAGES:])
        messages = messages[:MAX_MESSAGES]
        messages[-1] += f"\n...and {hidden} more new jobs"
    return messages


def _post(client: httpx.Client, url: str, payload: dict, what: str) -> None:
    """POST and fail with a message that never contains the URL (Telegram puts its token there)."""
    try:
        client.post(url, json=payload).raise_for_status()
    except httpx.HTTPError as exc:
        status = getattr(getattr(exc, "response", None), "status_code", "no response")
        raise RuntimeError(f"{what} notification failed ({status})") from None


def notify(jobs: list[Job], client: httpx.Client) -> list[str]:
    """Send new jobs to every channel configured through environment variables."""
    channels = []
    messages = format_messages(jobs)
    discord = os.environ.get("DISCORD_WEBHOOK_URL")
    token, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    for text in messages:
        if discord:
            _post(client, discord, {"content": text}, "discord")
        if token and chat:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            _post(client, url, {"chat_id": chat, "text": text}, "telegram")
    if discord:
        channels.append("discord")
    if token and chat:
        channels.append("telegram")
    return channels
