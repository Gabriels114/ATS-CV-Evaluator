import pytest

from ats_evaluator.scoring.engine import score
from ats_evaluator.reporting.json_export import to_dict


def test_pipeline_produces_valid_report(senior_backend_cv, senior_python_jd):
    report = score(senior_backend_cv, senior_python_jd)
    assert report.total_score > 0
    assert len(report.dimensions) == 7
    assert report.scoring_version == "1.0"


def test_json_export_is_serializable(senior_backend_cv, senior_python_jd):
    report = score(senior_backend_cv, senior_python_jd)
    data = to_dict(report)
    assert isinstance(data["total_score"], float)
    assert isinstance(data["dimensions"], list)
    assert len(data["dimensions"]) == 7


def test_suggestions_generated_for_low_scores(senior_python_jd, sample_contact, sample_parse_quality):
    import dataclasses
    from ats_evaluator.domain.cv import CVData
    weak_cv = CVData(
        full_name="Weak Candidate",
        contact=sample_contact,
        summary=None,
        hard_skills=("cobol",),
        soft_skills=(),
        experiences=(),
        education=(),
        certifications=(),
        raw_text="Weak Candidate\nCobol developer",
        parse_quality=sample_parse_quality,
    )
    report = score(weak_cv, senior_python_jd)
    assert len(report.suggestions) > 0
    assert report.total_score < 50.0
