"""Extracts structured JobDescription data from raw JD text using local NLP only."""

from __future__ import annotations

import re
from typing import Final

from ...domain.enums import SeniorityLevel
from ...domain.job import JobDescription
from .section_detector import detect_sections
from .skills_db import match_hard_skills, match_soft_skills

_TITLE_LABEL_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:job\s+title|position|role|title)\s*:\s*(.+)$", re.IGNORECASE
)

_SENIORITY_PATTERNS: Final[tuple[tuple[SeniorityLevel, tuple[str, ...]], ...]] = (
    (SeniorityLevel.PRINCIPAL, ("principal", "distinguished", "architect", "vp ", "director", "head of")),
    (SeniorityLevel.STAFF,     ("staff", "tech lead", "lead ")),
    (SeniorityLevel.SENIOR,    ("senior", "sr.", "sr ")),
    (SeniorityLevel.MID,       ("mid", "mid-level", "ssr", "semi-senior", "intermediate")),
    (SeniorityLevel.JUNIOR,    ("junior", "jr.", "entry level", "entry-level", "associate")),
    (SeniorityLevel.INTERN,    ("intern", "internship", "trainee", "practicante")),
)

_REQUIRED_KEYWORDS: Final[tuple[str, ...]] = (
    "required", "must have", "you must", "requirements",
    "qualifications", "you will need", "essential",
)

_PREFERRED_KEYWORDS: Final[tuple[str, ...]] = (
    "preferred", "nice to have", "bonus", "plus",
    "desirable", "ideal candidate", "we'd love",
)

_YEARS_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"(\d+)\s*-\s*\d+\s+years?", re.IGNORECASE),
    re.compile(r"minimum\s+(\d+)\s+years?", re.IGNORECASE),
    re.compile(r"at\s+least\s+(\d+)\s+years?", re.IGNORECASE),
    re.compile(r"(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)", re.IGNORECASE),
)

_EDUCATION_DEGREES: Final[tuple[str, ...]] = ("phd", "master", "bachelor", "associate", "degree")

_EDUCATION_FIELDS: Final[tuple[str, ...]] = (
    "computer science", "software engineering", "information technology",
    "engineering", "mathematics", "data science", "related field",
)

_BULLET_RE: Final[re.Pattern[str]] = re.compile(r"^[•●\-\*]\s+")


def _extract_title(raw_text: str) -> str:
    """Returns the job title from the first labeled field or first non-empty line."""
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        label_match = _TITLE_LABEL_RE.match(stripped)
        if label_match:
            return label_match.group(1).strip()
        return re.sub(
            r"^(?:job\s+title|position|role|title)\s*:\s*", "", stripped, flags=re.IGNORECASE
        )
    return ""


def _detect_seniority(text: str) -> SeniorityLevel:
    """Scans text for seniority keywords; highest-priority match wins."""
    lowered = text.lower()
    for level, keywords in _SENIORITY_PATTERNS:
        if any(kw in lowered for kw in keywords):
            return level
    return SeniorityLevel.MID


_PREFERRED_LINE_RE: Final = re.compile(
    r"^(?:nice\s+to\s+have|preferred|bonus|plus|desirable)\s*:?",
    re.IGNORECASE,
)
_REQUIRED_LINE_RE: Final = re.compile(
    r"^(?:must\s+have|required|requirements|qualifications|essential)\s*:?",
    re.IGNORECASE,
)


def _split_required_preferred(text: str) -> tuple[str, str]:
    """
    Splits into (required_block, preferred_block).
    Handles both paragraph-level and inline-section formats
    ('Nice to have: FastAPI, Redis' on its own line).
    """
    required_parts: list[str] = []
    preferred_parts: list[str] = []
    current_mode = "required"

    for line in text.splitlines():
        stripped = line.strip()
        if _PREFERRED_LINE_RE.match(stripped):
            current_mode = "preferred"
            # Include the content after the colon on the same line
            after = _PREFERRED_LINE_RE.sub("", stripped).strip().lstrip(":").strip()
            if after:
                preferred_parts = [*preferred_parts, after]
            continue
        if _REQUIRED_LINE_RE.match(stripped):
            current_mode = "required"
            after = _REQUIRED_LINE_RE.sub("", stripped).strip().lstrip(":").strip()
            if after:
                required_parts = [*required_parts, after]
            continue

        if current_mode == "preferred":
            preferred_parts = [*preferred_parts, line]
        else:
            required_parts = [*required_parts, line]

    return "\n".join(required_parts), "\n".join(preferred_parts)


def _extract_years_experience(text: str) -> int | None:
    """Returns the lowest years-of-experience number found in text, or None if none is present.

    Note: returns the minimum of all matches, which may reflect a per-skill requirement
    rather than the overall role requirement when multiple year counts appear.
    """
    found: list[int] = []
    for pattern in _YEARS_PATTERNS:
        for match in pattern.finditer(text):
            try:
                found = [*found, int(match.group(1))]
            except (ValueError, IndexError):
                continue
    return min(found) if found else None


def _extract_education(text: str) -> tuple[str, ...]:
    """Returns recognized degree types and field names found in text."""
    lowered = text.lower()
    degrees = [d for d in _EDUCATION_DEGREES if d in lowered]
    fields = [f for f in _EDUCATION_FIELDS if f in lowered]
    return tuple(degrees + fields)


def _extract_responsibilities(sections: dict[str, str], raw_text: str) -> tuple[str, ...]:
    """Extracts up to 15 bulleted lines from the experience section or full text."""
    source = sections.get("experience", "") or raw_text
    results: list[str] = []

    for line in source.splitlines():
        stripped = line.strip()
        if _BULLET_RE.match(stripped):
            cleaned = _BULLET_RE.sub("", stripped).strip()
            if cleaned:
                results = [*results, cleaned]
        if len(results) >= 15:
            break

    return tuple(results)


def extract_jd(raw_text: str) -> JobDescription:
    """
    Extracts structured JD data using local NLP only — no external API calls.
    """
    if not isinstance(raw_text, str):
        raw_text = str(raw_text)

    try:
        sections = detect_sections(raw_text)
    except Exception:
        sections = {}

    title = _extract_title(raw_text)

    # Check title first; fall back to full-text scan
    seniority = _detect_seniority(title) if title else SeniorityLevel.MID
    if seniority is SeniorityLevel.MID:
        seniority = _detect_seniority(raw_text)

    required_block, preferred_block = _split_required_preferred(raw_text)
    required_skills_set = set(match_hard_skills(required_block))
    preferred_skills_set = set(match_hard_skills(preferred_block)) - required_skills_set

    education_text = sections.get("education", "") or raw_text

    return JobDescription(
        title=title,
        seniority=seniority,
        required_hard_skills=tuple(sorted(required_skills_set)),
        preferred_hard_skills=tuple(sorted(preferred_skills_set)),
        soft_skills=tuple(sorted(set(match_soft_skills(raw_text)))),
        min_years_experience=_extract_years_experience(raw_text),
        required_education=_extract_education(education_text),
        responsibilities=_extract_responsibilities(sections, raw_text),
        raw_text=raw_text,
    )
