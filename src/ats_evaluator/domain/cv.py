from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class ContactInfo:
    """Immutable contact details extracted from a CV."""

    email: str | None
    phone: str | None
    location: str | None
    linkedin: str | None
    github: str | None


@dataclass(frozen=True, slots=True)
class ParseQuality:
    """Document parse-quality signal used downstream by formatters and scorers."""

    page_count: int
    has_images_only: bool
    tables_detected: bool
    estimated_char_density: float  # chars / page


@dataclass(frozen=True, slots=True)
class WorkExperience:
    """A single work-history entry parsed from a CV."""

    title: str
    company: str
    start_date: date | None
    end_date: date | None  # None means current role
    description: str
    technologies: tuple[str, ...]
    achievements: tuple[str, ...]
    quantified_metrics: tuple[str, ...]  # "$2M", "30%", "10x" etc.


@dataclass(frozen=True, slots=True)
class Education:
    """A single education record parsed from a CV."""

    degree: str
    field: str
    institution: str
    graduation_year: int | None


@dataclass(frozen=True, slots=True)
class CVData:
    """Fully structured, immutable representation of an extracted CV."""

    full_name: str | None
    contact: ContactInfo
    summary: str | None
    hard_skills: tuple[str, ...]
    soft_skills: tuple[str, ...]
    experiences: tuple[WorkExperience, ...]
    education: tuple[Education, ...]
    certifications: tuple[str, ...]
    raw_text: str
    parse_quality: ParseQuality
