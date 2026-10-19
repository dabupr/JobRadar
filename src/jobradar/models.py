from __future__ import annotations

from dataclasses import dataclass

from jobradar.places import fold, location_matches


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

    def matches(
        self, query: str | None = None, remote: bool = False, city: str | None = None
    ) -> bool:
        if remote and not self.remote:
            return False
        if city and not location_matches(self.location, city):
            return False
        if query:
            haystack = fold(f"{self.title} {self.company} {self.location}")
            return all(word in haystack for word in fold(query).split())
        return True
