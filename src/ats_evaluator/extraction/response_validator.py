from datetime import date, datetime
from typing import Any

from dateutil import parser as dateparser

from ..errors import InvalidExtractionError

_DEFAULT_DT = datetime(2000, 1, 1)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return dateparser.parse(value, default=_DEFAULT_DT).date()
    except Exception:
        return None


def validate_cv_response(raw: dict[str, Any]) -> dict[str, Any]:
    required = [
        "full_name", "contact", "summary", "hard_skills",
        "soft_skills", "experiences", "education", "certifications",
    ]
    missing = [f for f in required if f not in raw]
    if missing:
        raise InvalidExtractionError(f"CV extraction missing fields: {missing}")

    hard_skills = list({s.lower().strip() for s in raw.get("hard_skills", []) if s})
    soft_skills = list({s.lower().strip() for s in raw.get("soft_skills", []) if s})

    experiences = []
    for exp in raw.get("experiences", []):
        experiences.append({
            **exp,
            "start_date": _parse_date(exp.get("start_date")),
            "end_date": _parse_date(exp.get("end_date")),
            "technologies": [t.lower().strip() for t in exp.get("technologies", [])],
            "achievements": exp.get("achievements", []),
            "quantified_metrics": exp.get("quantified_metrics", []),
        })

    return {
        **raw,
        "hard_skills": hard_skills,
        "soft_skills": soft_skills,
        "experiences": experiences,
    }


def validate_jd_response(raw: dict[str, Any]) -> dict[str, Any]:
    required = [
        "title", "seniority", "required_hard_skills", "preferred_hard_skills",
        "soft_skills", "min_years_experience", "required_education", "responsibilities",
    ]
    missing = [f for f in required if f not in raw]
    if missing:
        raise InvalidExtractionError(f"JD extraction missing fields: {missing}")

    return {
        **raw,
        "required_hard_skills": [s.lower().strip() for s in raw.get("required_hard_skills", [])],
        "preferred_hard_skills": [s.lower().strip() for s in raw.get("preferred_hard_skills", [])],
        "soft_skills": [s.lower().strip() for s in raw.get("soft_skills", [])],
    }
