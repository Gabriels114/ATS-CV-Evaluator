"""Local CV extractor — no external API calls. Uses regex, skills taxonomy, and optional spaCy."""

from __future__ import annotations

import re
from datetime import date
from typing import Final

from ...domain.cv import CVData, ContactInfo, Education, ParseQuality, WorkExperience
from .metrics_extractor import extract_metrics
from .section_detector import detect_sections
from .skills_db import match_hard_skills, match_soft_skills

# ---------------------------------------------------------------------------
# spaCy optional import
# ---------------------------------------------------------------------------
try:
    import spacy as _spacy

    _nlp = _spacy.load("en_core_web_sm")
except Exception:
    _nlp = None

# ---------------------------------------------------------------------------
# Compiled regexes
# ---------------------------------------------------------------------------
_RE_EMAIL: Final = re.compile(r"[\w.+\-]+@[\w\-]+\.[\w.\-]+")
_RE_PHONE: Final = re.compile(r"(\+?\d[\d\s\-().]{7,14}\d)")
_RE_LINKEDIN: Final = re.compile(r"linkedin\.com/in/[\w\-]+", re.IGNORECASE)
_RE_GITHUB: Final = re.compile(r"github\.com/[\w\-]+", re.IGNORECASE)
_RE_LOCATION: Final = re.compile(
    r"\b([A-Z][a-zA-Z\s]+),\s*([A-Z][a-zA-Z\s]{2,})\b"
)

_JOB_TITLE_KEYWORDS: Final = re.compile(
    r"\b(engineer|developer|manager|analyst|designer|scientist|architect|"
    r"lead|director|head|intern|consultant|specialist|coordinator|officer|"
    r"president|vp|cto|ceo|cfo|coo)\b",
    re.IGNORECASE,
)

_RE_DEGREE: Final = re.compile(
    r"\b(phd|ph\.d|doctor|master|msc|mba|bachelor|bsc|beng|"
    r"licenciatura|ingenier[oa]|ingenier[íi]a|associate)\b",
    re.IGNORECASE,
)
_RE_GRAD_YEAR: Final = re.compile(r"\b(19[7-9]\d|20[0-2]\d|2030)\b")
_RE_FIELD: Final = re.compile(
    r"\b(computer|software|data|engineering|science|mathematics|physics|"
    r"economics|business|information|systems|cybersecurity|ai|machine learning)\b",
    re.IGNORECASE,
)

_MONTHS_SHORT: Final = (
    "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
)
_MONTHS_LONG: Final = (
    "January|February|March|April|May|June|July|August|"
    "September|October|November|December"
)
_RE_DATE_RANGE: Final = re.compile(
    rf"(?:{_MONTHS_SHORT}|{_MONTHS_LONG})[\s,]*(\d{{4}})?\s*[-–]\s*"
    r"((?:" + _MONTHS_SHORT + r"|" + _MONTHS_LONG + r")[\s,]*\d{4}|present|current|now|\d{4})",
    re.IGNORECASE,
)
_RE_YEAR_RANGE: Final = re.compile(
    r"\b(20\d{2})\s*[-–]\s*(20\d{2}|present|current|now)\b",
    re.IGNORECASE,
)
_RE_BULLET: Final = re.compile(r"^[\s]*[•\-●*▪▸►>]+\s+")
_RE_COMPANY_SEPARATOR: Final = re.compile(r"\s*[\|@]\s*|\bat\s+", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Contact extraction
# ---------------------------------------------------------------------------

def _extract_contact(text: str) -> ContactInfo:
    email_m = _RE_EMAIL.search(text)
    phone_m = _RE_PHONE.search(text)
    linkedin_m = _RE_LINKEDIN.search(text)
    github_m = _RE_GITHUB.search(text)

    location: str | None = None
    first_lines = "\n".join(text.splitlines()[:5])
    loc_m = _RE_LOCATION.search(first_lines)
    if loc_m:
        location = loc_m.group(0).strip()

    return ContactInfo(
        email=email_m.group(0) if email_m else None,
        phone=phone_m.group(1).strip() if phone_m else None,
        location=location,
        linkedin=linkedin_m.group(0) if linkedin_m else None,
        github=github_m.group(0) if github_m else None,
    )


# ---------------------------------------------------------------------------
# Full name extraction
# ---------------------------------------------------------------------------

def _looks_like_name_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if _RE_EMAIL.search(stripped) or _RE_PHONE.search(stripped):
        return False
    if re.search(r"https?://|www\.|linkedin|github", stripped, re.IGNORECASE):
        return False
    words = stripped.split()
    if not (2 <= len(words) <= 4):
        return False
    return all(re.match(r"^[A-ZÁÉÍÓÚÑÜ][a-záéíóúñü\-']+$", w) for w in words)


def _extract_full_name(text: str, spacy_doc: object | None) -> str | None:
    if spacy_doc is not None:
        for ent in spacy_doc.ents:
            if ent.label_ == "PERSON":
                return ent.text.strip()

    for line in text.splitlines()[:10]:
        if _looks_like_name_line(line):
            return line.strip()
    return None


# ---------------------------------------------------------------------------
# Date parsing helpers
# ---------------------------------------------------------------------------

_MONTH_MAP: Final[dict[str, int]] = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    "january": 1, "february": 2, "march": 3, "april": 4, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10,
    "november": 11, "december": 12,
}


def _parse_date_token(token: str) -> date | None:
    token = token.strip().lower()
    if token in ("present", "current", "now"):
        return None
    year_m = re.search(r"20\d{2}", token)
    if not year_m:
        return None
    year = int(year_m.group(0))
    for month_name, month_num in _MONTH_MAP.items():
        if month_name in token:
            return date(year, month_num, 1)
    return date(year, 1, 1)


def _extract_dates(block: str) -> tuple[date | None, date | None]:
    m = _RE_DATE_RANGE.search(block)
    if m:
        full = m.group(0)
        parts = re.split(r"[-–]", full, maxsplit=1)
        if len(parts) == 2:
            return _parse_date_token(parts[0]), _parse_date_token(parts[1])

    m2 = _RE_YEAR_RANGE.search(block)
    if m2:
        start_yr = int(m2.group(1))
        end_token = m2.group(2)
        end = None if end_token.lower() in ("present", "current", "now") else date(int(end_token), 1, 1)
        return date(start_yr, 1, 1), end

    return None, None


# ---------------------------------------------------------------------------
# Experience block parsing
# ---------------------------------------------------------------------------

def _split_experience_blocks(exp_text: str) -> list[str]:
    blocks = re.split(r"\n{2,}", exp_text.strip())
    if len(blocks) <= 1:
        lines = exp_text.splitlines()
        current: list[str] = []
        result: list[list[str]] = []
        for line in lines:
            if current and _JOB_TITLE_KEYWORDS.search(line) and not _RE_BULLET.match(line):
                result.append(current)
                current = [line]
            else:
                current = [*current, line]
        if current:
            result.append(current)
        return ["\n".join(b) for b in result if b]
    return [b.strip() for b in blocks if b.strip()]


def _extract_company_from_block(lines: list[str], title_idx: int, spacy_doc: object | None) -> str:
    if spacy_doc is not None:
        for ent in spacy_doc.ents:
            if ent.label_ == "ORG":
                return ent.text.strip()

    title_line = lines[title_idx] if title_idx < len(lines) else ""
    sep_m = _RE_COMPANY_SEPARATOR.search(title_line)
    if sep_m:
        candidate = title_line[sep_m.end():].strip()
        # Strip trailing date ranges like "| Jan 2021 - Present"
        candidate = _RE_DATE_RANGE.sub("", candidate).strip()
        candidate = _RE_YEAR_RANGE.sub("", candidate).strip().rstrip("|·,- ")
        if candidate:
            return candidate

    if title_idx + 1 < len(lines):
        next_line = lines[title_idx + 1].strip()
        if next_line and not _RE_BULLET.match(next_line):
            return next_line

    return ""


def _parse_experience_block(block: str) -> WorkExperience | None:
    lines = [l for l in block.splitlines() if l.strip()]
    if not lines:
        return None

    title = ""
    title_idx = 0
    for i, line in enumerate(lines):
        if _JOB_TITLE_KEYWORDS.search(line) and not _RE_BULLET.match(line):
            title = line.strip()
            title_idx = i
            break
    if not title and lines:
        title = lines[0].strip()

    doc = None
    if _nlp is not None:
        try:
            doc = _nlp(block[:500])
        except Exception:
            doc = None

    company = _extract_company_from_block(lines, title_idx, doc)
    start_date, end_date = _extract_dates(block)

    achievements: list[str] = []
    for line in lines:
        if _RE_BULLET.match(line):
            cleaned = _RE_BULLET.sub("", line).strip()
            if cleaned:
                achievements = [*achievements, cleaned]

    description = block.strip()
    metrics = tuple(extract_metrics("\n".join(achievements) if achievements else block))
    technologies = tuple(match_hard_skills(block))

    return WorkExperience(
        title=title,
        company=company,
        start_date=start_date,
        end_date=end_date,
        description=description,
        technologies=technologies,
        achievements=tuple(achievements),
        quantified_metrics=metrics,
    )


# ---------------------------------------------------------------------------
# Education parsing
# ---------------------------------------------------------------------------

def _parse_education_block(block: str) -> Education | None:
    degree_m = _RE_DEGREE.search(block)
    if not degree_m:
        return None

    degree = degree_m.group(0).strip()
    grad_year: int | None = None
    year_m = _RE_GRAD_YEAR.search(block)
    if year_m:
        grad_year = int(year_m.group(0))

    field = ""
    field_m = _RE_FIELD.search(block)
    if field_m:
        line_with_field = next(
            (l for l in block.splitlines() if _RE_FIELD.search(l)), ""
        )
        field = line_with_field.strip()

    institution = ""
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if _RE_DEGREE.search(stripped):
            continue
        if _RE_GRAD_YEAR.search(stripped) and len(stripped) <= 10:
            continue
        if _RE_FIELD.search(stripped):
            continue
        institution = stripped
        break

    return Education(
        degree=degree,
        field=field,
        institution=institution,
        graduation_year=grad_year,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_cv(raw_text: str, quality: ParseQuality) -> CVData:
    """
    Extracts structured CV data using local NLP only — no external API calls.
    Uses regex, skills taxonomy, and optionally spaCy if installed.
    """
    sections = detect_sections(raw_text)

    doc = None
    if _nlp is not None:
        try:
            doc = _nlp(raw_text[:1000])
        except Exception:
            doc = None

    contact = _extract_contact(raw_text)
    full_name = _extract_full_name(raw_text, doc)
    summary = sections.get("summary") or None

    # Fallback to full text when sections aren't detected (no headers in CV)
    _fallback = raw_text
    skills_text = " ".join(filter(None, [
        sections.get("skills", ""),
        sections.get("experience", ""),
        sections.get("other", ""),
    ])) or _fallback
    hard_skills = tuple(match_hard_skills(skills_text))
    # Soft skills are often scattered in bullet points — scan full text
    soft_skills = tuple(match_soft_skills(raw_text))

    experiences: list[WorkExperience] = []
    exp_text = sections.get("experience", "") or sections.get("other", "")
    if exp_text:
        for block in _split_experience_blocks(exp_text):
            parsed = _parse_experience_block(block)
            if parsed is not None:
                experiences = [*experiences, parsed]

    education: list[Education] = []
    edu_text = sections.get("education", "")
    if edu_text:
        for block in re.split(r"\n{2,}", edu_text.strip()):
            if block.strip():
                parsed_edu = _parse_education_block(block.strip())
                if parsed_edu is not None:
                    education = [*education, parsed_edu]
    else:
        # No section header — extract only lines containing a degree keyword
        degree_lines: list[str] = []
        all_lines = raw_text.splitlines()
        for i, line in enumerate(all_lines):
            if _RE_DEGREE.search(line):
                context = "\n".join(all_lines[max(0, i - 1):i + 3])
                parsed_edu = _parse_education_block(context)
                if parsed_edu is not None:
                    education = [*education, parsed_edu]

    certifications: tuple[str, ...] = ()
    cert_text = sections.get("certifications", "")
    if cert_text:
        cert_lines = [
            line.strip()
            for line in cert_text.splitlines()
            if line.strip() and not re.match(r"^[-=]{3,}$", line.strip())
        ]
        certifications = tuple(cert_lines)

    return CVData(
        full_name=full_name,
        contact=contact,
        summary=summary,
        hard_skills=hard_skills,
        soft_skills=soft_skills,
        experiences=tuple(experiences),
        education=tuple(education),
        certifications=certifications,
        raw_text=raw_text,
        parse_quality=quality,
    )
