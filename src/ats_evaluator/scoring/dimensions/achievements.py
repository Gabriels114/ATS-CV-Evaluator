from types import MappingProxyType

from ...domain.cv import CVData
from ...domain.job import JobDescription
from ...domain.scoring import DimensionScore
from ..weights import WEIGHTS


class AchievementsScorer:
    """Scores the quantity of quantified achievements across all work experiences."""

    name = "achievements"
    weight = WEIGHTS["achievements"]

    def score(self, cv: CVData, jd: JobDescription) -> DimensionScore:
        """10 points per quantified metric, capped at 100."""
        total_metrics = sum(len(exp.quantified_metrics) for exp in cv.experiences)

        # Each quantified metric is worth 10 points, capped at 100
        raw_score = min(100.0, total_metrics * 10.0)

        return DimensionScore(
            name=self.name,
            weight=self.weight,
            raw_score=round(raw_score, 2),
            weighted_score=round(raw_score * self.weight, 2),
            details=MappingProxyType({"total_quantified_metrics": total_metrics}),
        )
