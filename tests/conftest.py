from datetime import date
from types import MappingProxyType

import pytest

from ats_evaluator.domain.cv import CVData, ContactInfo, Education, ParseQuality, WorkExperience
from ats_evaluator.domain.enums import SeniorityLevel
from ats_evaluator.domain.job import JobDescription


@pytest.fixture
def sample_contact() -> ContactInfo:
    return ContactInfo(
        email="dev@example.com",
        phone=None,
        location="Mexico City",
        linkedin=None,
        github="github.com/dev",
    )


@pytest.fixture
def sample_parse_quality() -> ParseQuality:
    return ParseQuality(
        page_count=2,
        has_images_only=False,
        tables_detected=False,
        estimated_char_density=1500.0,
    )


@pytest.fixture
def senior_backend_cv(sample_contact, sample_parse_quality) -> CVData:
    exp1 = WorkExperience(
        title="Senior Backend Engineer",
        company="Acme Corp",
        start_date=date(2021, 1, 1),
        end_date=None,
        description="Led backend development using Python and PostgreSQL.",
        technologies=("python", "postgresql", "docker", "kubernetes", "fastapi"),
        achievements=("Reduced latency by 40%", "Led team of 5 engineers"),
        quantified_metrics=("40%", "5 engineers"),
    )
    exp2 = WorkExperience(
        title="Backend Engineer",
        company="Beta Inc",
        start_date=date(2018, 3, 1),
        end_date=date(2020, 12, 31),
        description="Built REST APIs and microservices.",
        technologies=("python", "django", "redis", "postgresql"),
        achievements=("Increased throughput by 2x",),
        quantified_metrics=("2x",),
    )
    return CVData(
        full_name="Jane Developer",
        contact=sample_contact,
        summary="Senior backend engineer with 6+ years in Python.",
        hard_skills=("python", "postgresql", "docker", "kubernetes", "fastapi", "django", "redis"),
        soft_skills=("leadership", "communication", "teamwork"),
        experiences=(exp1, exp2),
        education=(Education(
            degree="Bachelor of Science",
            field="Computer Science",
            institution="UNAM",
            graduation_year=2017,
        ),),
        certifications=("AWS Certified Developer",),
        raw_text="Jane Developer\nExperience\nSenior Backend Engineer...",
        parse_quality=sample_parse_quality,
    )


@pytest.fixture
def senior_python_jd() -> JobDescription:
    return JobDescription(
        title="Senior Python Engineer",
        seniority=SeniorityLevel.SENIOR,
        required_hard_skills=("python", "postgresql", "docker", "kubernetes"),
        preferred_hard_skills=("fastapi", "redis", "terraform"),
        soft_skills=("communication", "leadership"),
        min_years_experience=5,
        required_education=("bachelor", "computer science"),
        responsibilities=("Design microservices", "Lead code reviews"),
        raw_text="We are looking for a Senior Python Engineer...",
    )
