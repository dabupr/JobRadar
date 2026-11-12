from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from jobradar.models import Job
from jobradar.places import fold, location_matches
from jobradar.seniority import LEVELS


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


class ProfileError(ValueError):
    pass


def _list_of_strings(value: object, field: str, path: str | Path) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ProfileError(f"{path}: '{field}' must be a list of strings")
    return value


def load_profile(path: str | Path) -> Profile:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ProfileError(f"{path}: profile must be a mapping")
    keywords = _list_of_strings(data.get("keywords"), "keywords", path)
    exclude = _list_of_strings(data.get("exclude"), "exclude", path)
    cities = _list_of_strings(data.get("cities"), "cities", path)
    levels = _list_of_strings(data.get("levels"), "levels", path)
    invalid = [level for level in levels if level not in LEVELS]
    if invalid:
        raise ProfileError(
            f"{path}: unsupported levels {invalid!r} (expected: {', '.join(LEVELS)})"
        )
    remote = data.get("remote", False)
    if not isinstance(remote, bool):
        raise ProfileError(f"{path}: 'remote' must be true/false")
    return Profile(
        keywords=keywords,
        exclude=exclude,
        cities=cities,
        remote=remote,
        levels=levels,
    )
