from __future__ import annotations

import unicodedata

# Every spelling that should count as the same place. Keys and values are accent-free lowercase.
CITY_ALIASES: dict[str, list[str]] = {
    "barcelona": [
        "barcelona", "bcn", "catalonia", "catalunya", "cataluna", "badalona", "hospitalet",
        "sant cugat", "cornella", "sabadell", "terrassa", "sitges", "mataro",
    ],
    "madrid": ["madrid", "mad", "alcobendas", "pozuelo", "las rozas"],
    "valencia": ["valencia"],
}

# Remote jobs whose location says one of these are open to people living in Spain.
SPAIN_WORDS = ["spain", "espana", "iberia", "emea", "europe", "eu", "worldwide", "anywhere"]


def fold(text: str) -> str:
    """Lowercase and strip accents so 'Cataluña' and 'catalunya' compare cleanly."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).casefold()


def city_terms(city: str) -> list[str]:
    needle = fold(city).strip()
    for key, names in CITY_ALIASES.items():
        group = [fold(n) for n in names]
        if needle == key or needle in group:
            return group
    return [needle]


def location_matches(location: str, city: str) -> bool:
    place = fold(location)
    return any(term in place for term in city_terms(city))


def open_to_spain(location: str, remote: bool) -> bool:
    if not remote:
        return False
    words = set(fold(location).replace(",", " ").replace("-", " ").replace("/", " ").split())
    return bool(words & set(SPAIN_WORDS))
