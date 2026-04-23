import pytest

from ats_evaluator.domain.cv import ParseQuality
from ats_evaluator.extraction.local.cv_extractor import extract_cv
from ats_evaluator.extraction.local.jd_extractor import extract_jd
from ats_evaluator.extraction.local.metrics_extractor import extract_metrics
from ats_evaluator.extraction.local.section_detector import detect_sections
from ats_evaluator.extraction.local.skills_db import match_hard_skills, match_soft_skills
from ats_evaluator.extraction.mode import ExtractionMode


# ── section_detector ──────────────────────────────────────────────────────────

def test_detect_sections_basic():
    text = "EXPERIENCE\nSoftware Engineer at ACME\n\nEDUCATION\nBSc Computer Science"
    sections = detect_sections(text)
    assert "experience" in sections
    assert "education" in sections


def test_detect_sections_no_headers():
    text = "Just some plain text without any headers."
    sections = detect_sections(text)
    assert "other" in sections
    assert "Just some plain text" in sections["other"]


def test_detect_sections_skills():
    text = "SKILLS\nPython, Docker, Kubernetes\nEXPERIENCE\nEngineer at Corp"
    sections = detect_sections(text)
    assert "skills" in sections
    assert "Python" in sections["skills"]


# ── metrics_extractor ─────────────────────────────────────────────────────────

def test_extract_metrics_percentage():
    assert "30%" in extract_metrics("Improved performance by 30%")


def test_extract_metrics_dollar():
    assert "$2M" in extract_metrics("Generated $2M in revenue")


def test_extract_metrics_multiplier():
    result = extract_metrics("Increased throughput 5x")
    assert any("5x" in m.lower() or "5" in m for m in result)


def test_extract_metrics_empty():
    assert extract_metrics("No metrics here at all") == []


def test_extract_metrics_multiple():
    result = extract_metrics("Revenue grew 40% and saved $500K")
    assert len(result) >= 2


# ── skills_db ────────────────────────────────────────────────────────────────

def test_match_hard_skills_basic():
    skills = match_hard_skills("Python developer with Docker and Kubernetes experience")
    assert "python" in skills
    assert "docker" in skills
    assert "kubernetes" in skills


def test_match_hard_skills_alias():
    skills = match_hard_skills("We use k8s and postgres in production")
    assert "kubernetes" in skills
    assert "postgresql" in skills


def test_match_hard_skills_no_false_positive():
    # "java" should not match inside "javascript"
    skills = match_hard_skills("We use JavaScript exclusively")
    assert "java" not in skills


def test_match_soft_skills():
    skills = match_soft_skills("Strong leadership and communication skills required")
    assert "leadership" in skills
    assert "communication" in skills


def test_match_soft_skills_empty():
    skills = match_soft_skills("Python Docker Kubernetes AWS")
    assert isinstance(skills, list)


# ── ExtractionMode ────────────────────────────────────────────────────────────

def test_extraction_mode_values():
    assert ExtractionMode.LOCAL.value == "local"
    assert ExtractionMode.LLM.value == "llm"


def test_extraction_mode_from_string():
    assert ExtractionMode("local") == ExtractionMode.LOCAL
    assert ExtractionMode("llm") == ExtractionMode.LLM


# ── Local CV extractor ────────────────────────────────────────────────────────

SAMPLE_CV = """
Jane Developer
jane@example.com | github.com/janedev | Mexico City, Mexico

SUMMARY
Senior backend engineer with 6 years in Python.

EXPERIENCE

Senior Backend Engineer
Acme Corp | Jan 2021 - Present
• Led migration to microservices, reducing latency by 40%
• Managed team of 5 engineers
Technologies: Python, FastAPI, PostgreSQL, Docker, Kubernetes

Backend Engineer
Beta Inc | Mar 2018 - Dec 2020
• Increased throughput by 2x
Technologies: Python, Django, Redis

EDUCATION

Bachelor of Science in Computer Science
UNAM - 2017

SKILLS
Python, FastAPI, Django, PostgreSQL, Docker, Kubernetes, Redis
Leadership, Communication, Teamwork

CERTIFICATIONS
AWS Certified Developer Associate
"""

@pytest.fixture
def sample_quality():
    return ParseQuality(
        page_count=1, has_images_only=False,
        tables_detected=False, estimated_char_density=1500.0,
    )


def test_local_cv_contact(sample_quality):
    cv = extract_cv(SAMPLE_CV, sample_quality)
    assert cv.contact.email == "jane@example.com"
    assert cv.contact.github is not None


def test_local_cv_hard_skills(sample_quality):
    cv = extract_cv(SAMPLE_CV, sample_quality)
    assert "python" in cv.hard_skills
    assert "docker" in cv.hard_skills


def test_local_cv_soft_skills(sample_quality):
    cv = extract_cv(SAMPLE_CV, sample_quality)
    assert "leadership" in cv.soft_skills


def test_local_cv_experiences(sample_quality):
    cv = extract_cv(SAMPLE_CV, sample_quality)
    assert len(cv.experiences) >= 1
    assert cv.experiences[0].title != ""


def test_local_cv_metrics(sample_quality):
    cv = extract_cv(SAMPLE_CV, sample_quality)
    all_metrics = [m for exp in cv.experiences for m in exp.quantified_metrics]
    assert len(all_metrics) >= 1


def test_local_cv_education(sample_quality):
    cv = extract_cv(SAMPLE_CV, sample_quality)
    assert len(cv.education) >= 1
    assert cv.education[0].graduation_year == 2017


def test_local_cv_certifications(sample_quality):
    cv = extract_cv(SAMPLE_CV, sample_quality)
    assert len(cv.certifications) >= 1


def test_local_cv_is_immutable(sample_quality):
    import dataclasses
    cv = extract_cv(SAMPLE_CV, sample_quality)
    with pytest.raises(dataclasses.FrozenInstanceError):
        cv.full_name = "Hacker"  # type: ignore


def test_local_cv_empty_text(sample_quality):
    cv = extract_cv("", sample_quality)
    assert cv.hard_skills == ()
    assert cv.experiences == ()


# ── Local JD extractor ────────────────────────────────────────────────────────

SAMPLE_JD = """
Senior Python Engineer

We are looking for a Senior Python Engineer with 5+ years of experience.

Requirements:
• Python (required)
• PostgreSQL (required)
• Docker (required)
• Kubernetes (required)

Nice to have:
• Terraform
• Redis

Responsibilities:
• Design and implement microservices
• Lead code reviews
• Mentor junior engineers

Education: Bachelor's degree in Computer Science or related field.
"""


def test_local_jd_title():
    jd = extract_jd(SAMPLE_JD)
    assert "Python" in jd.title or "Engineer" in jd.title


def test_local_jd_required_skills():
    jd = extract_jd(SAMPLE_JD)
    assert "python" in jd.required_hard_skills


def test_local_jd_min_years():
    jd = extract_jd(SAMPLE_JD)
    assert jd.min_years_experience == 5


def test_local_jd_seniority():
    from ats_evaluator.domain.enums import SeniorityLevel
    jd = extract_jd(SAMPLE_JD)
    assert jd.seniority == SeniorityLevel.SENIOR


def test_local_jd_responsibilities():
    jd = extract_jd(SAMPLE_JD)
    assert len(jd.responsibilities) >= 1


def test_local_jd_immutable():
    import dataclasses
    jd = extract_jd(SAMPLE_JD)
    with pytest.raises(dataclasses.FrozenInstanceError):
        jd.title = "Hacked"  # type: ignore


def test_local_jd_empty_text():
    jd = extract_jd("")
    assert jd.required_hard_skills == ()
    assert jd.min_years_experience is None
