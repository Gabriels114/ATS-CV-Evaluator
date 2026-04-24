from datetime import date
from types import MappingProxyType

from ...domain.cv import CVData
from ...domain.job import JobDescription
from ...domain.scoring import DimensionScore
from ...extraction.local.section_detector import detect_sections
from ...extraction.local.skills_db import match_hard_skills
from ..keyword_matcher import skills_missing, skills_overlap
from ..recency import recency_factor
from ..weights import WEIGHTS

_PLACEMENT_PREMIUM_BOOST = 1.3
_PLACEMENT_DEFAULT = 1.0


def _premium_skill_set(cv: CVData) -> frozenset[str]:
    """Build the set of skills that appear in the CV summary or skills section (parsed once).

    Falls back to an empty frozenset on any detection error, which causes all
    skills to receive the default (non-boosted) multiplier.
    """
    try:
        sections = detect_sections(cv.raw_text)
    except Exception:
        return frozenset()

    premium_text = sections.get("summary", "") + " " + sections.get("skills", "")
    return frozenset(match_hard_skills(premium_text))


def _skill_recency_factor(skill: str, cv: CVData, today: date) -> float:
    """Recency multiplier (0.3–1.0) from the most recent experience that lists the skill.

    Returns 1.0 when the skill is absent from all experiences (e.g. skills-section only).
    """
    factors = [
        recency_factor(exp.end_date, today)
        for exp in cv.experiences
        if skill in exp.technologies
    ]
    return max(factors) if factors else 1.0


def _boosted_score(skills: tuple[str, ...], matched: set[str], cv: CVData) -> float:
    """Placement- and recency-weighted coverage score (0–100).

    `detect_sections` and `match_hard_skills` are called once for the whole batch,
    not once per skill, keeping complexity O(skills) instead of O(skills * text_lines).
    The pre-clamp maximum is `_PLACEMENT_PREMIUM_BOOST * 1.0 * 100 = 130`; the
    `min(..., 100)` clamp keeps the final value in the 0–100 range.
    """
    total = max(len(skills), 1)
    today = date.today()
    premium_skills = _premium_skill_set(cv)

    weighted_sum = sum(
        (_PLACEMENT_PREMIUM_BOOST if skill in premium_skills else _PLACEMENT_DEFAULT)
        * _skill_recency_factor(skill, cv, today)
        for skill in matched
    )
    return min((weighted_sum / total) * 100, 100.0)


class HardSkillsScorer:
    """Scores CV hard-skill coverage against JD required and preferred skills."""

    name = "hard_skills"
    weight = WEIGHTS["hard_skills"]

    def score(self, cv: CVData, jd: JobDescription) -> DimensionScore:
        """Combined required (70%) + preferred (30%) skill score with placement and recency boosts."""
        required = jd.required_hard_skills
        preferred = jd.preferred_hard_skills

        matched_required = skills_overlap(cv.hard_skills, required)
        matched_preferred = skills_overlap(cv.hard_skills, preferred)

        required_score_boosted = _boosted_score(required, matched_required, cv)
        preferred_score_boosted = (
            _boosted_score(preferred, matched_preferred, cv) if preferred else 100.0
        )

        raw_score = round(
            required_score_boosted * 0.7 + preferred_score_boosted * 0.3, 2
        )

        return DimensionScore(
            name=self.name,
            weight=self.weight,
            raw_score=raw_score,
            weighted_score=round(raw_score * self.weight, 2),
            details=MappingProxyType({
                "matched_required": sorted(matched_required),
                "matched_preferred": sorted(matched_preferred),
                "missing_required": skills_missing(cv.hard_skills, required),
                "required_score": round(required_score_boosted, 2),
                "preferred_score": round(preferred_score_boosted, 2),
                "placement_weighting_applied": True,
                "skill_recency_applied": True,
            }),
        )
