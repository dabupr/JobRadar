from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from jobradar.models import Job

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL,
    url TEXT NOT NULL,
    source TEXT NOT NULL,
    remote INTEGER NOT NULL,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL
)
"""

INSERT_SQL = """
INSERT INTO jobs (id, title, company, location, url, source, remote, first_seen, last_seen)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(id) DO UPDATE SET
    title=excluded.title,
    company=excluded.company,
    location=excluded.location,
    url=excluded.url,
    source=excluded.source,
    remote=excluded.remote,
    last_seen=excluded.last_seen
"""


class Store:
    def __init__(self, path: str):
        self.db = sqlite3.connect(path)
        self.db.execute(SCHEMA)

    def is_empty(self) -> bool:
        return self.db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 0

    def upsert(self, jobs: list[Job], now: str | None = None) -> list[Job]:
        """Save the jobs and return the ones never seen before."""
        now = now or datetime.now(timezone.utc).isoformat(timespec="seconds")
        new = []
        seen_this_run = set()
        for job in jobs:
            if job.id in seen_this_run:
                continue
            seen_this_run.add(job.id)
            cursor = self.db.execute("SELECT first_seen FROM jobs WHERE id = ?", (job.id,))
            exists = cursor.fetchone() is not None
            self.db.execute(
                INSERT_SQL,
                (
                    job.id,
                    job.title,
                    job.company,
                    job.location,
                    job.url,
                    job.source,
                    int(job.remote),
                    now,
                    now,
                ),
            )
            if not exists:
                new.append(job)
        self.db.commit()
        return new

    def close(self) -> None:
        self.db.close()
