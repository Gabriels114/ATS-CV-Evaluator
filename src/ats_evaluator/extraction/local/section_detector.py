"""Detects and splits CV/JD text into named sections using header pattern matching."""

import re
from typing import Final

SECTION_PATTERNS: Final[dict[str, list[str]]] = {
    "experience": [
        "experience",
        "work experience",
        "employment",
        "work history",
        "professional experience",
        "career history",
    ],
    "education": [
        "education",
        "academic background",
        "qualifications",
        "academic history",
    ],
    "skills": [
        "skills",
        "technical skills",
        "core competencies",
        "expertise",
        "technologies",
        "stack",
    ],
    "summary": [
        "summary",
        "profile",
        "about",
        "objective",
        "professional summary",
        "career objective",
    ],
    "certifications": [
        "certifications",
        "certificates",
        "credentials",
        "licenses",
    ],
    "projects": [
        "projects",
        "personal projects",
        "side projects",
        "portfolio",
    ],
}

# Maps each lowercase header variant to its canonical section name.
_VARIANT_TO_CANONICAL: Final[dict[str, str]] = {
    variant.lower(): canonical
    for canonical, variants in SECTION_PATTERNS.items()
    for variant in variants
}

_HEADER_RE: Final[re.Pattern[str]] = re.compile(
    r"^[ \t]*(.+?)[ \t]*(?::|-{2,})?[ \t]*$"
)


def _identify_section(line: str) -> str | None:
    """Returns the canonical section name if the line is a recognized section header, else None."""
    stripped = line.strip()
    if not stripped:
        return None

    # ALL CAPS multi-word lines (contain non-alpha chars like spaces) are strong header candidates.
    # Single-word all-caps headers (e.g. "SKILLS") fall through to the _HEADER_RE / exact-match paths.
    if stripped == stripped.upper() and len(stripped) > 2 and not stripped.isalpha():
        candidate = stripped.rstrip(":- \t").lower()
        if candidate in _VARIANT_TO_CANONICAL:
            return _VARIANT_TO_CANONICAL[candidate]

    # Lines ending with ":" or "---" separators.
    m = _HEADER_RE.match(stripped)
    if m:
        candidate = m.group(1).strip().lower().rstrip(":-")
        if candidate in _VARIANT_TO_CANONICAL:
            return _VARIANT_TO_CANONICAL[candidate]

    # Plain line that exactly matches a variant (case-insensitive).
    candidate = stripped.lower()
    if candidate in _VARIANT_TO_CANONICAL:
        return _VARIANT_TO_CANONICAL[candidate]

    return None


def detect_sections(text: str) -> dict[str, str]:
    """
    Splits CV/JD text into named sections.

    Returns dict with keys like 'experience', 'education', 'skills', 'summary',
    'certifications', 'projects', 'objective', 'other'.
    Values are the text content of each section (header line excluded).
    """
    lines = text.splitlines()

    sections: dict[str, list[str]] = {}
    current_section: str = "__preamble__"
    section_lines: list[str] = []

    for line in lines:
        detected = _identify_section(line)
        if detected is not None:
            # Flush the previous section's accumulated lines.
            if section_lines:
                existing = sections.get(current_section, [])
                sections[current_section] = existing + section_lines
            current_section = detected
            section_lines = []
        else:
            section_lines = [*section_lines, line]

    # Flush the last section.
    if section_lines:
        existing = sections.get(current_section, [])
        sections[current_section] = existing + section_lines

    # Merge preamble into 'other' if no real section consumed it.
    named_sections = {k: v for k, v in sections.items() if k != "__preamble__"}

    if not named_sections:
        return {"other": text}

    preamble_lines = sections.get("__preamble__", [])
    if preamble_lines:
        preamble_text = "\n".join(preamble_lines).strip()
        if preamble_text:
            existing_other = named_sections.get("other", [])
            named_sections["other"] = [preamble_text, *existing_other] if existing_other else [preamble_text]

    return {
        section: "\n".join(content_lines).strip()
        for section, content_lines in named_sections.items()
        if "\n".join(content_lines).strip()
    }
