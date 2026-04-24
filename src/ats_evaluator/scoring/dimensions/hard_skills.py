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


def _placement_boost(skill: str, cv: CVData) -> float:
    """
    Returns 1.3 if the skill appears in the summary or dedicated skills section,
    1.0 otherwise. Falls back to 1.0 on any detection error.
    """
    try:
        sections = detect_sections(cv.raw_text)
    except Exception:
        return _PLACEMENT_DEFAULT

    premium_text = sections.get("summary", "") + " " + sections.get("skills", "")
    premium_skills = match_hard_skills(premium_text)
    return _PLACEMENT_PREMIUM_BOOST if skill in premium_skills else _PLACEMENT_DEFAULT


def _skill_recency_factor(skill: str, cv: CVData) -> float:
    """
    Returns recency multiplier (0.3–1.0) based on the most recent mention across
    work experiences. Returns 1.0 when the skill is not found in any experience
    (e.g. listed only in a skills section).
    """
    today = date.today()
    factors = [
        recency_factor(exp.end_date, today)
        for exp in cv.experiences
        if skill in exp.technologies
    ]
    return max(factors) if factors else 1.0


def _boosted_score(skills: tuple[str, ...], matched: set[str], cv: CVData) -> float:
    """
    Returns a placement- and recency-weighted coverage score (0–100).
    Only matched skills contribute; each is scaled by its two multipliers.
    """
    total = max(len(skills), 1)
    weighted_sum = sum(
        _placement_boost(skill, cv) * _skill_recency_factor(skill, cv)
        for skill in matched
    )
    return min((weighted_sum / total) * 100, 100.0)


class HardSkillsScorer:
    name = "hard_skills"
    weight = WEIGHTS["hard_skills"]

    def score(self, cv: CVData, jd: JobDescription) -> DimensionScore:
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
