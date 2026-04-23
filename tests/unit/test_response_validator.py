import pytest

from ats_evaluator.errors import InvalidExtractionError
from ats_evaluator.extraction.response_validator import validate_cv_response, validate_jd_response


_VALID_CV = {
    "full_name": "Jane Dev",
    "contact": {"email": "j@e.com", "phone": None, "location": None, "linkedin": None, "github": None},
    "summary": "Python dev",
    "hard_skills": ["Python", "Docker", "Python"],  # duplicate
    "soft_skills": ["Leadership"],
    "experiences": [
        {
            "title": "Engineer", "company": "ACME",
            "start_date": "2020-01-01", "end_date": None,
            "description": "Built stuff",
            "technologies": ["Python", "PostgreSQL"],
            "achievements": ["Did 30%"],
            "quantified_metrics": ["30%"],
        }
    ],
    "education": [{"degree": "BSc", "field": "CS", "institution": "UNAM", "graduation_year": 2019}],
    "certifications": ["AWS"],
}

_VALID_JD = {
    "title": "Senior Engineer",
    "seniority": "senior",
    "required_hard_skills": ["Python", "Docker"],
    "preferred_hard_skills": ["Kubernetes"],
    "soft_skills": ["Communication"],
    "min_years_experience": 5,
    "required_education": ["bachelor"],
    "responsibilities": ["Build services"],
}


def test_validate_cv_normalizes_skills():
    result = validate_cv_response(_VALID_CV)
    assert all(s == s.lower() for s in result["hard_skills"])


def test_validate_cv_deduplicates():
    result = validate_cv_response(_VALID_CV)
    assert result["hard_skills"].count("python") == 1


def test_validate_cv_parses_dates():
    result = validate_cv_response(_VALID_CV)
    exp = result["experiences"][0]
    assert exp["start_date"] is not None
    assert exp["end_date"] is None


def test_validate_cv_missing_fields():
    with pytest.raises(InvalidExtractionError, match="missing fields"):
        validate_cv_response({"full_name": "Jane"})


def test_validate_jd_normalizes_skills():
    result = validate_jd_response(_VALID_JD)
    assert all(s == s.lower() for s in result["required_hard_skills"])


def test_validate_jd_missing_fields():
    with pytest.raises(InvalidExtractionError, match="missing fields"):
        validate_jd_response({"title": "Engineer"})
