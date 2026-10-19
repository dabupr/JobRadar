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


class Store:
    def __init__(self, path: str):
        self.db = sqlite3.connect(path)
        self.db.execute(SCHEMA)

    def is_empty(self) -> bool:
        return self.db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 0

    def upsert(self, jobs: list[Job], now: str | None = None) -> list[Job]:
        """Save the jobs and return the ones never seen before."""
        now = now or datetime.now(timezone.utc).isoformat(timespec="seconds")
        known = {row[0] for row in self.db.execute("SELECT id FROM jobs")}
        new = []
        for job in jobs:
            if job.id in known:
                self.db.execute("UPDATE jobs SET last_seen = ? WHERE id = ?", (now, job.id))
                continue
            known.add(job.id)
            new.append(job)
            self.db.execute(
                "INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (job.id, job.title, job.company, job.location, job.url, job.source,
                 int(job.remote), now, now),
            )
        self.db.commit()
        return new

    def close(self) -> None:
        self.db.close()
