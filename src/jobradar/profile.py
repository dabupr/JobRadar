from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from jobradar.models import Job
from jobradar.places import fold, location_matches


@dataclass
class Profile:
    keywords: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    cities: list[str] = field(default_factory=list)
    remote: bool = False
    levels: list[str] = field(default_factory=list)

    def accepts(self, job: Job) -> bool:
        text = fold(f"{job.title} {job.company}")
        if any(fold(word) in text for word in self.exclude):
            return False
        if self.keywords and not any(fold(word) in text for word in self.keywords):
            return False
        if self.levels and job.level not in self.levels:
            return False
        in_city = not self.cities or any(location_matches(job.location, c) for c in self.cities)
        return in_city or (self.remote and job.remote)


def load_profile(path: str | Path) -> Profile:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return Profile(
        keywords=data.get("keywords", []),
        exclude=data.get("exclude", []),
        cities=data.get("cities", []),
        remote=bool(data.get("remote", False)),
        levels=data.get("levels", []),
    )
