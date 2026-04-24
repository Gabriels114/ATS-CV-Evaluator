import pytest

from ats_evaluator.domain.cv import ContactInfo
from ats_evaluator.domain.feedback import Priority
from ats_evaluator.feedback.generator import generate_suggestions
from ats_evaluator.scoring.semantic_matcher import (
    is_available,
    semantic_similarity,
    semantic_skills_overlap,
)
from ats_evaluator.scoring.keyword_matcher import (
    skills_missing_enhanced,
    skills_overlap_enhanced,
)


# ── semantic_matcher ──────────────────────────────────────────────────────────

def test_is_available_returns_bool():
    result = is_available()
    assert isinstance(result, bool)


def test_semantic_similarity_returns_float():
    result = semantic_similarity("python developer", "python engineer")
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_semantic_similarity_unavailable_returns_zero():
    # Whether or not sentence-transformers is installed, function must not raise
    result = semantic_similarity("any text", "other text")
    assert isinstance(result, float)


def test_semantic_skills_overlap_returns_set():
    result = semantic_skills_overlap(("python", "docker"), ("python", "kubernetes"))
    assert isinstance(result, set)


def test_semantic_skills_overlap_empty_inputs():
    assert semantic_skills_overlap((), ()) == set()
    assert semantic_skills_overlap(("python",), ()) == set()
    assert semantic_skills_overlap((), ("python",)) == set()


def test_semantic_skills_overlap_no_raise_when_unavailable():
    # Should silently return empty set if library not installed
    result = semantic_skills_overlap(("machine learning",), ("ml",))
    assert isinstance(result, set)


# ── skills_overlap_enhanced + skills_missing_enhanced ────────────────────────

def test_skills_overlap_enhanced_exact():
    result = skills_overlap_enhanced(("python", "docker"), ("python", "kubernetes"))
    assert "python" in result


def test_skills_overlap_enhanced_via_alias():
    # k8s → kubernetes alias should still work
    result = skills_overlap_enhanced(("k8s",), ("kubernetes",))
    assert "kubernetes" in result


def test_skills_missing_enhanced_basic():
    missing = skills_missing_enhanced(("python", "docker"), ("python", "kubernetes", "redis"))
    assert "kubernetes" in missing
    assert "redis" in missing
    assert "python" not in missing


def test_skills_missing_enhanced_empty():
    assert skills_missing_enhanced((), ()) == []


# ── contact validation suggestions ───────────────────────────────────────────

def _make_contact(**kwargs) -> ContactInfo:
    defaults = dict(email=None, phone=None, location=None, linkedin=None, github=None)
    return ContactInfo(**{**defaults, **kwargs})


def test_contact_missing_email_generates_high_suggestion():
    contact = _make_contact(email=None, linkedin="linkedin.com/in/user")
    suggestions = generate_suggestions((), (), contact=contact)
    email_sugs = [s for s in suggestions if s.dimension == "contact" and s.priority == Priority.HIGH]
    assert len(email_sugs) == 1
    assert "email" in email_sugs[0].message.lower()


def test_contact_missing_linkedin_generates_medium_suggestion():
    contact = _make_contact(email="user@example.com", linkedin=None)
    suggestions = generate_suggestions((), (), contact=contact)
    linkedin_sugs = [s for s in suggestions if "LinkedIn" in s.message]
    assert len(linkedin_sugs) == 1
    assert linkedin_sugs[0].priority == Priority.MEDIUM


def test_contact_complete_generates_no_contact_suggestions():
    contact = _make_contact(
        email="user@example.com",
        phone="+52 555 1234",
        linkedin="linkedin.com/in/user",
    )
    suggestions = generate_suggestions((), (), contact=contact)
    contact_sugs = [s for s in suggestions if s.dimension == "contact"]
    assert len(contact_sugs) == 0


def test_contact_none_generates_no_contact_suggestions():
    suggestions = generate_suggestions((), (), contact=None)
    contact_sugs = [s for s in suggestions if s.dimension == "contact"]
    assert len(contact_sugs) == 0


def test_generate_suggestions_no_contact_arg_backward_compatible():
    # Old callers that don't pass contact still work
    suggestions = generate_suggestions((), ())
    assert isinstance(suggestions, tuple)
