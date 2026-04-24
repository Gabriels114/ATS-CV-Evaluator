from datetime import date
from types import MappingProxyType

from ...domain.cv import CVData, WorkExperience
from ...domain.job import JobDescription
from ...domain.scoring import DimensionScore
from ..keyword_matcher import skills_overlap
from ..recency import recency_factor
from ..weights import WEIGHTS


def _experience_years(exp: WorkExperience, today: date) -> float:
    """Duration of a work experience in fractional years, clamped to zero for future start dates."""
    if exp.start_date is None:
        return 0.0
    end = exp.end_date or today
    return max(0.0, (end - exp.start_date).days / 365.25)


def _relevance(exp: WorkExperience, jd: JobDescription) -> float:
    """Fraction of combined JD skills that appear in the experience's technology list."""
    all_jd_skills = jd.required_hard_skills + jd.preferred_hard_skills
    if not all_jd_skills:
        return 0.5
    matched = skills_overlap(exp.technologies, all_jd_skills)
    return len(matched) / len(all_jd_skills)


class ExperienceScorer:
    """Scores total relevant experience weighted by skill overlap and recency."""

    name = "experience"
    weight = WEIGHTS["experience"]

    def score(self, cv: CVData, jd: JobDescription) -> DimensionScore:
        """Weighted-relevant-years vs JD minimum; 10 effective years = 100 when no minimum set."""
        today = date.today()
        weighted_years = 0.0

        for exp in cv.experiences:
            years = _experience_years(exp, today)
            relevance = _relevance(exp, jd)
            recency = recency_factor(exp.end_date, today)
            weighted_years += years * relevance * recency

        min_years = jd.min_years_experience or 0
        if min_years > 0:
            years_score = min(100.0, (weighted_years / min_years) * 100)
        else:
            years_score = min(100.0, weighted_years * 10)  # 10 effective years = 100%

        return DimensionScore(
            name=self.name,
            weight=self.weight,
            raw_score=round(years_score, 2),
            weighted_score=round(years_score * self.weight, 2),
            details=MappingProxyType({
                "weighted_relevant_years": round(weighted_years, 2),
                "min_years_required": min_years,
            }),
        )
