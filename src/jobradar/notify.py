from __future__ import annotations

import os

import httpx

from jobradar.models import Job

LIMIT = 1800


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
    return messages


def notify(jobs: list[Job], client: httpx.Client) -> list[str]:
    """Send new jobs to every channel configured through environment variables."""
    channels = []
    messages = format_messages(jobs)
    discord = os.environ.get("DISCORD_WEBHOOK_URL")
    token, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    for text in messages:
        if discord:
            client.post(discord, json={"content": text}).raise_for_status()
        if token and chat:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            client.post(url, json={"chat_id": chat, "text": text}).raise_for_status()
    if discord:
        channels.append("discord")
    if token and chat:
        channels.append("telegram")
    return channels
