from ats_evaluator.scoring.dimensions.hard_skills import HardSkillsScorer


def test_perfect_match(senior_backend_cv, senior_python_jd):
    scorer = HardSkillsScorer()
    result = scorer.score(senior_backend_cv, senior_python_jd)
    # All required skills match (100%); preferred partially matched + placement/recency boost
    assert result.raw_score >= 80.0
    assert result.weighted_score == pytest.approx(result.raw_score * scorer.weight, abs=0.02)


def test_zero_match(senior_backend_cv, senior_python_jd):
    import dataclasses
    cv = dataclasses.replace(senior_backend_cv, hard_skills=("cobol", "fortran"))
    result = HardSkillsScorer().score(cv, senior_python_jd)
    assert result.raw_score < 20.0


def test_partial_match(senior_backend_cv, senior_python_jd):
    import dataclasses
    cv = dataclasses.replace(senior_backend_cv, hard_skills=("python", "docker"))
    result = HardSkillsScorer().score(cv, senior_python_jd)
    assert 30.0 < result.raw_score < 80.0


def test_weighted_score_is_raw_times_weight(senior_backend_cv, senior_python_jd):
    scorer = HardSkillsScorer()
    result = scorer.score(senior_backend_cv, senior_python_jd)
    assert result.weighted_score == pytest.approx(result.raw_score * scorer.weight, abs=0.02)


import pytest
