from __future__ import annotations

from pathlib import Path

import yaml

from jobradar.connectors import CONNECTORS
from jobradar.feeds import FEEDS


class ConfigError(ValueError):
    pass


def _load(path: str | Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def load_companies(path: str | Path) -> list[dict]:
    data = _load(path)
    companies = data.get("companies", [])
    if not isinstance(companies, list):
        raise ConfigError(f"{path}: 'companies' must be a list")
    valid_ats = set(CONNECTORS)
    errors = []
    cleaned = []
    for idx, entry in enumerate(companies, start=1):
        ctx = f"{path}:companies[{idx}]"
        if not isinstance(entry, dict):
            errors.append(f"{ctx} must be a mapping")
            continue
        name = entry.get("name")
        ats = entry.get("ats")
        slug = entry.get("slug")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{ctx}.name must be a non-empty string")
        if not isinstance(ats, str) or not ats.strip():
            errors.append(f"{ctx}.ats must be a non-empty string")
        elif ats not in valid_ats:
            errors.append(f"{ctx}.ats unknown value {ats!r} (expected one of: {', '.join(sorted(valid_ats))})")
        if not isinstance(slug, str) or not slug.strip():
            errors.append(f"{ctx}.slug must be a non-empty string")
        if not errors or not any(err.startswith(ctx) for err in errors):
            cleaned.append(entry)
    if errors:
        raise ConfigError("invalid companies.yaml:\n- " + "\n- ".join(errors))
    return cleaned


def load_feeds(path: str | Path) -> list[str]:
    data = _load(path)
    feeds = data.get("feeds", [])
    if not isinstance(feeds, list):
        raise ConfigError(f"{path}: 'feeds' must be a list")
    errors = []
    valid = set(FEEDS)
    for idx, feed in enumerate(feeds, start=1):
        ctx = f"{path}:feeds[{idx}]"
        if not isinstance(feed, str) or not feed.strip():
            errors.append(f"{ctx} must be a non-empty string")
            continue
        if feed not in valid:
            errors.append(f"{ctx} unknown value {feed!r} (expected one of: {', '.join(sorted(valid))})")
    if errors:
        raise ConfigError("invalid companies.yaml:\n- " + "\n- ".join(errors))
    return feeds
