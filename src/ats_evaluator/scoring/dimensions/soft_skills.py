from types import MappingProxyType

from ...domain.cv import CVData
from ...domain.job import JobDescription
from ...domain.scoring import DimensionScore
from ..keyword_matcher import skills_overlap
from ..weights import WEIGHTS


class SoftSkillsScorer:
    name = "soft_skills"
    weight = WEIGHTS["soft_skills"]

    def score(self, cv: CVData, jd: JobDescription) -> DimensionScore:
        if not jd.soft_skills:
            raw_score = 100.0
            matched: set[str] = set()
        else:
            matched = skills_overlap(cv.soft_skills, jd.soft_skills)
            raw_score = (len(matched) / len(jd.soft_skills)) * 100

        return DimensionScore(
            name=self.name,
            weight=self.weight,
            raw_score=round(raw_score, 2),
            weighted_score=round(raw_score * self.weight, 2),
            details=MappingProxyType({"matched_soft_skills": sorted(matched)}),
        )
