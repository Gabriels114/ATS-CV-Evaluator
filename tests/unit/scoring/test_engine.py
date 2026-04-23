import pytest

from ats_evaluator.scoring.engine import score
from ats_evaluator.scoring.weights import WEIGHTS


def test_total_equals_sum_of_weighted_dims(senior_backend_cv, senior_python_jd):
    report = score(senior_backend_cv, senior_python_jd)
    expected = sum(d.weighted_score for d in report.dimensions)
    assert report.total_score == pytest.approx(expected, abs=0.01)


def test_all_dimensions_present(senior_backend_cv, senior_python_jd):
    report = score(senior_backend_cv, senior_python_jd)
    dim_names = {d.name for d in report.dimensions}
    assert dim_names == set(WEIGHTS.keys())


def test_score_is_between_0_and_100(senior_backend_cv, senior_python_jd):
    report = score(senior_backend_cv, senior_python_jd)
    assert 0 <= report.total_score <= 100


def test_strong_cv_scores_above_70(senior_backend_cv, senior_python_jd):
    report = score(senior_backend_cv, senior_python_jd)
    assert report.total_score >= 70.0


def test_weights_sum_to_one():
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9
