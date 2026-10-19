from __future__ import annotations

import re

from jobradar.places import fold

LEVELS = ["intern", "junior", "mid", "senior", "lead", "manager"]

# First match wins, so "Senior Engineering Manager" is a manager and "Staff Engineer" a lead.
# Titles are folded first, so accents and case don't matter (sènior, Júnior, prácticas...).
_WORDS = {
    "intern": ["intern", "interns", "internship", "trainee", "working student", "werkstudent",
               "apprentice", "co-op", "becari", "becaria", "becarios", "practicas", "practiques",
               "stagiaire", "alternance"],
    "manager": ["manager", "managers", "director", "directora", "directeur", "head of", "vp",
                "vice president", "cto", "cfo", "coo", "ceo", "responsable", "gerente", "gerent",
                "jefe", "jefa", "cap de"],
    "lead": ["staff", "principal", "lead(?! generation)", "tech lead", "team lead"],
    "senior": ["senior", "sr", "snr", "experienced"],
    "junior": ["junior", "jr", "entry level", "entry-level", "graduate", "new grad"],
}
_RULES = [(level, rf"\b({'|'.join(words)})\b") for level, words in _WORDS.items()]
_COMPILED = [(level, re.compile(pattern)) for level, pattern in _RULES]


def level_of(title: str) -> str:
    """Guess the seniority from a job title. Titles with no marker count as mid."""
    text = fold(title)
    for level, pattern in _COMPILED:
        if pattern.search(text):
            return level
    return "mid"
