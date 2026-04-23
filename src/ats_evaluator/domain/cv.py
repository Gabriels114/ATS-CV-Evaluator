from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class ContactInfo:
    email: str | None
    phone: str | None
    location: str | None
    linkedin: str | None
    github: str | None


@dataclass(frozen=True, slots=True)
class ParseQuality:
    page_count: int
    has_images_only: bool
    tables_detected: bool
    estimated_char_density: float  # chars / page


@dataclass(frozen=True, slots=True)
class WorkExperience:
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
    degree: str
    field: str
    institution: str
    graduation_year: int | None


@dataclass(frozen=True, slots=True)
class CVData:
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
