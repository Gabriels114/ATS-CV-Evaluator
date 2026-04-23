"""Loads the skills taxonomy and performs word-boundary-aware matching against text."""

import json
import re
from pathlib import Path
from typing import Final

_TAXONOMY_PATH: Final[Path] = Path(__file__).parent.parent.parent / "data" / "skills_taxonomy.json"

# Module-level singletons — loaded once on first access.
_hard_skills: dict[str, list[str]] | None = None
_soft_skills: list[str] | None = None


def _load_taxonomy() -> tuple[dict[str, list[str]], list[str]]:
    global _hard_skills, _soft_skills  # noqa: PLW0603

    if _hard_skills is not None and _soft_skills is not None:
        return _hard_skills, _soft_skills

    try:
        raw = _TAXONOMY_PATH.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Skills taxonomy not found at {_TAXONOMY_PATH}. "
            "Ensure the data directory is properly installed."
        ) from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed skills taxonomy JSON: {exc}") from exc

    if "hard_skills" not in data or "soft_skills" not in data:
        raise ValueError("Taxonomy must contain 'hard_skills' and 'soft_skills' keys.")

    _hard_skills = data["hard_skills"]
    _soft_skills = data["soft_skills"]
    return _hard_skills, _soft_skills


def _word_boundary_search(term: str, text: str) -> bool:
    """Returns True if `term` appears as a whole word in `text` (case-insensitive)."""
    pattern = r"\b" + re.escape(term) + r"\b"
    return bool(re.search(pattern, text, re.IGNORECASE))


def match_hard_skills(text: str) -> list[str]:
    """Returns list of canonical hard skill names found in text (lowercase)."""
    hard_skills, _ = _load_taxonomy()

    matched: list[str] = []
    for canonical, aliases in hard_skills.items():
        all_terms = [canonical, *aliases]
        if any(_word_boundary_search(term, text) for term in all_terms):
            matched = [*matched, canonical]

    return matched


def match_soft_skills(text: str) -> list[str]:
    """Returns list of soft skill names found in text (lowercase)."""
    _, soft_skills = _load_taxonomy()

    matched: list[str] = []
    for skill in soft_skills:
        if _word_boundary_search(skill, text):
            matched = [*matched, skill.lower()]

    return matched
