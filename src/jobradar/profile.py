from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from jobradar.models import Job


@dataclass
class Profile:
    keywords: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    cities: list[str] = field(default_factory=list)
    remote: bool = False

    def accepts(self, job: Job) -> bool:
        text = f"{job.title} {job.company}".lower()
        if any(word.lower() in text for word in self.exclude):
            return False
        if self.keywords and not any(word.lower() in text for word in self.keywords):
            return False
        place = job.location.lower()
        in_city = not self.cities or any(city.lower() in place for city in self.cities)
        return in_city or (self.remote and job.remote)


def load_profile(path: str | Path) -> Profile:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return Profile(
        keywords=data.get("keywords", []),
        exclude=data.get("exclude", []),
        cities=data.get("cities", []),
        remote=bool(data.get("remote", False)),
    )
