from dataclasses import dataclass

from .enums import SeniorityLevel


@dataclass(frozen=True, slots=True)
class JobDescription:
    """Immutable structured representation of an extracted job description."""

    title: str
    seniority: SeniorityLevel
    required_hard_skills: tuple[str, ...]
    preferred_hard_skills: tuple[str, ...]
    soft_skills: tuple[str, ...]
    min_years_experience: int | None
    required_education: tuple[str, ...]  # e.g. ["bachelor's", "computer science"]
    responsibilities: tuple[str, ...]
    raw_text: str
