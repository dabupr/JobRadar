from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path

from jobradar.models import Job
from jobradar.places import CITY_ALIASES, SPAIN_WORDS, fold


def write_site(jobs: list[Job], out: str | Path) -> Path:
    """Write the static job board: index.html next to a jobs.json with every job."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "aliases": {k: [fold(n) for n in v] for k, v in CITY_ALIASES.items()},
        "spain_words": SPAIN_WORDS,
        "jobs": [asdict(job) for job in sorted(jobs, key=lambda j: (j.company, j.title))],
    }
    (out / "jobs.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    html = resources.files("jobradar.web").joinpath("index.html").read_text(encoding="utf-8")
    (out / "index.html").write_text(html, encoding="utf-8")
    return out
