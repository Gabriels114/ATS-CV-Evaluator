import dataclasses
from datetime import date

import pytest

from ats_evaluator.domain.cv import CVData, WorkExperience
from ats_evaluator.domain.enums import SeniorityLevel
from ats_evaluator.domain.job import JobDescription
from ats_evaluator.scoring.dimensions.achievements import AchievementsScorer
from ats_evaluator.scoring.dimensions.education import EducationScorer
from ats_evaluator.scoring.dimensions.experience import ExperienceScorer
from ats_evaluator.scoring.dimensions.formatting import FormattingScorer
from ats_evaluator.scoring.dimensions.soft_skills import SoftSkillsScorer
from ats_evaluator.scoring.dimensions.title_alignment import TitleAlignmentScorer


# ── Achievements ──────────────────────────────────────────────────────────────

def test_achievements_zero(senior_backend_cv, senior_python_jd):
    cv = dataclasses.replace(
        senior_backend_cv,
        experiences=tuple(
            dataclasses.replace(e, quantified_metrics=()) for e in senior_backend_cv.experiences
        ),
    )
    result = AchievementsScorer().score(cv, senior_python_jd)
    assert result.raw_score == 0.0


def test_achievements_capped_at_100(senior_backend_cv, senior_python_jd):
    exp = dataclasses.replace(
        senior_backend_cv.experiences[0],
        quantified_metrics=tuple(f"{i}%" for i in range(20)),
    )
    cv = dataclasses.replace(senior_backend_cv, experiences=(exp,))
    result = AchievementsScorer().score(cv, senior_python_jd)
    assert result.raw_score == 100.0


def test_achievements_proportional(senior_backend_cv, senior_python_jd):
    exp = dataclasses.replace(
        senior_backend_cv.experiences[0], quantified_metrics=("30%", "2x", "$1M")
    )
    cv = dataclasses.replace(senior_backend_cv, experiences=(exp,))
    result = AchievementsScorer().score(cv, senior_python_jd)
    assert result.raw_score == 30.0


# ── Soft Skills ───────────────────────────────────────────────────────────────

def test_soft_skills_no_jd_requirements(senior_backend_cv, senior_python_jd):
    jd = dataclasses.replace(senior_python_jd, soft_skills=())
    result = SoftSkillsScorer().score(senior_backend_cv, jd)
    assert result.raw_score == 100.0


def test_soft_skills_partial_match(senior_backend_cv, senior_python_jd):
    jd = dataclasses.replace(senior_python_jd, soft_skills=("communication", "empathy", "leadership"))
    result = SoftSkillsScorer().score(senior_backend_cv, jd)
    # CV has communication + leadership → 2/3
    assert pytest.approx(result.raw_score, abs=1) == 66.67


# ── Title Alignment ───────────────────────────────────────────────────────────

def test_title_exact_seniority_match(senior_backend_cv, senior_python_jd):
    result = TitleAlignmentScorer().score(senior_backend_cv, senior_python_jd)
    assert result.raw_score == 100.0


def test_title_no_experience(senior_backend_cv, senior_python_jd):
    cv = dataclasses.replace(senior_backend_cv, experiences=())
    result = TitleAlignmentScorer().score(cv, senior_python_jd)
    assert result.raw_score == 50.0


def test_title_junior_vs_senior(senior_backend_cv, senior_python_jd):
    exp = dataclasses.replace(senior_backend_cv.experiences[0], title="Junior Developer")
    cv = dataclasses.replace(senior_backend_cv, experiences=(exp,))
    result = TitleAlignmentScorer().score(cv, senior_python_jd)
    assert result.raw_score <= 50.0


# ── Education ─────────────────────────────────────────────────────────────────

def test_education_no_cv_education(senior_backend_cv, senior_python_jd):
    cv = dataclasses.replace(senior_backend_cv, education=())
    result = EducationScorer().score(cv, senior_python_jd)
    assert result.raw_score == 0.0


def test_education_exceeds_requirement(senior_backend_cv, senior_python_jd):
    from ats_evaluator.domain.cv import Education
    cv = dataclasses.replace(
        senior_backend_cv,
        education=(Education(degree="PhD", field="Computer Science", institution="MIT", graduation_year=2019),),
    )
    result = EducationScorer().score(cv, senior_python_jd)
    assert result.raw_score >= 90.0


# ── Experience ────────────────────────────────────────────────────────────────

def test_experience_meets_minimum(senior_backend_cv, senior_python_jd):
    result = ExperienceScorer().score(senior_backend_cv, senior_python_jd)
    assert result.raw_score >= 70.0


def test_experience_no_roles(senior_backend_cv, senior_python_jd):
    cv = dataclasses.replace(senior_backend_cv, experiences=())
    result = ExperienceScorer().score(cv, senior_python_jd)
    assert result.raw_score == 0.0


# ── Formatting ────────────────────────────────────────────────────────────────

def test_formatting_clean_cv(senior_backend_cv, senior_python_jd):
    result = FormattingScorer().score(senior_backend_cv, senior_python_jd)
    assert result.raw_score >= 70.0
