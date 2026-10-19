from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    id: str
    title: str
    company: str
    location: str
    url: str
    source: str
    remote: bool = False
    updated_at: str | None = None

    def matches(self, query: str | None = None, remote: bool = False) -> bool:
        if remote and not self.remote:
            return False
        if query:
            haystack = f"{self.title} {self.company} {self.location}".lower()
            return all(word in haystack for word in query.lower().split())
        return True
