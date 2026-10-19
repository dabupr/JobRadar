from __future__ import annotations

from pathlib import Path

import yaml


def _load(path: str | Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def load_companies(path: str | Path) -> list[dict]:
    return _load(path).get("companies", [])


def load_feeds(path: str | Path) -> list[str]:
    return _load(path).get("feeds", [])
