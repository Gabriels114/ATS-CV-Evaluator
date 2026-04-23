from types import MappingProxyType

from ...domain.cv import CVData
from ...domain.job import JobDescription
from ...domain.scoring import DimensionScore
from ..keyword_matcher import skills_missing, skills_overlap
from ..weights import WEIGHTS


class HardSkillsScorer:
    name = "hard_skills"
    weight = WEIGHTS["hard_skills"]

    def score(self, cv: CVData, jd: JobDescription) -> DimensionScore:
        required = jd.required_hard_skills
        preferred = jd.preferred_hard_skills

        matched_required = skills_overlap(cv.hard_skills, required)
        matched_preferred = skills_overlap(cv.hard_skills, preferred)

        # Required skills count double
        required_score = (len(matched_required) / max(len(required), 1)) * 100
        preferred_score = (len(matched_preferred) / max(len(preferred), 1)) * 100 if preferred else 100.0

        raw_score = required_score * 0.7 + preferred_score * 0.3

        return DimensionScore(
            name=self.name,
            weight=self.weight,
            raw_score=round(raw_score, 2),
            weighted_score=round(raw_score * self.weight, 2),
            details=MappingProxyType({
                "matched_required": sorted(matched_required),
                "matched_preferred": sorted(matched_preferred),
                "missing_required": skills_missing(cv.hard_skills, required),
                "required_score": round(required_score, 2),
                "preferred_score": round(preferred_score, 2),
            }),
        )
