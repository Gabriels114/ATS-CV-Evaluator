import pytest

from ats_evaluator.scoring.keyword_matcher import exact_match, normalize, skills_missing, skills_overlap


@pytest.mark.parametrize("input_skill,expected", [
    ("Python",       "python"),
    ("JS",           "javascript"),
    ("k8s",          "kubernetes"),
    ("PostgreSQL",   "postgresql"),
    ("Postgres",     "postgresql"),
    ("TensorFlow",   "tensorflow"),
])
def test_normalize_aliases(input_skill, expected):
    assert normalize(input_skill) == expected


def test_exact_match_case_insensitive():
    assert exact_match("Python", "python")
    assert exact_match("JS", "javascript")
    assert not exact_match("java", "javascript")


def test_skills_overlap():
    cv = ("python", "docker", "js")
    jd = ("python", "kubernetes", "javascript")
    matched = skills_overlap(cv, jd)
    assert "python" in matched
    assert "javascript" in matched   # js → javascript alias


def test_skills_missing():
    cv = ("python", "docker")
    jd = ("python", "kubernetes", "redis")
    missing = skills_missing(cv, jd)
    assert "kubernetes" in missing
    assert "redis" in missing
    assert "python" not in missing
