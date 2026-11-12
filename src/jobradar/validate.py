from __future__ import annotations

import sys


def has_fields(item: object, required: tuple[str, ...], where: str, idx: int) -> bool:
    """True when the item has every required field. Otherwise print a warning so one bad
    record is skipped instead of breaking the whole source."""
    if not isinstance(item, dict):
        print(f"warning: {where} item {idx} is not an object", file=sys.stderr)
        return False
    missing = [field for field in required if not item.get(field)]
    if missing:
        print(f"warning: {where} item {idx} missing {', '.join(missing)}", file=sys.stderr)
        return False
    return True
