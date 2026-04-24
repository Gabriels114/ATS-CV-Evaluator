"""Loads the skills taxonomy and performs word-boundary-aware matching against text."""

import json
import re
from pathlib import Path
from typing import Final

_TAXONOMY_PATH: Final[Path] = Path(__file__).parent.parent.parent / "data" / "skills_taxonomy.json"

# ---------------------------------------------------------------------------
# Taxonomy cache — populated once at first call, never mutated afterwards.
# Stored as a tuple so the reference is immutable after assignment.
# ---------------------------------------------------------------------------
_TAXONOMY_CACHE: tuple[dict[str, re.Pattern[str]], tuple[tuple[str, re.Pattern[str]], ...]] | None = None


def _build_pattern(term: str) -> re.Pattern[str]:
    """Compiles a word-boundary pattern for a single skill term."""
    return re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)


def _load_taxonomy() -> tuple[dict[str, re.Pattern[str]], tuple[tuple[str, re.Pattern[str]], ...]]:
    """Returns (hard_skill_patterns, soft_skill_patterns), loading from disk only once."""
    global _TAXONOMY_CACHE  # noqa: PLW0603

    if _TAXONOMY_CACHE is not None:
        return _TAXONOMY_CACHE

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

    # Pre-compile one combined alternation pattern per canonical hard skill.
    hard_patterns: dict[str, re.Pattern[str]] = {}
    for canonical, aliases in data["hard_skills"].items():
        all_terms = [canonical, *aliases]
        combined = "|".join(re.escape(t) for t in all_terms)
        hard_patterns[canonical] = re.compile(r"\b(?:" + combined + r")\b", re.IGNORECASE)

    # Pre-compile one pattern per soft skill.
    soft_patterns: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
        (skill.lower(), _build_pattern(skill))
        for skill in data["soft_skills"]
    )

    _TAXONOMY_CACHE = (hard_patterns, soft_patterns)
    return _TAXONOMY_CACHE


def match_hard_skills(text: str) -> list[str]:
    """Returns list of canonical hard skill names found in text (lowercase)."""
    hard_patterns, _ = _load_taxonomy()
    return [canonical for canonical, pattern in hard_patterns.items() if pattern.search(text)]


def match_soft_skills(text: str) -> list[str]:
    """Returns list of soft skill names found in text (lowercase)."""
    _, soft_patterns = _load_taxonomy()
    return [skill for skill, pattern in soft_patterns if pattern.search(text)]
