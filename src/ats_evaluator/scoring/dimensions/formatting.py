from types import MappingProxyType

from ...domain.cv import CVData
from ...domain.job import JobDescription
from ...domain.scoring import DimensionScore
from ...parsers.format_quality import assess_parseability
from ..weights import WEIGHTS


class FormattingScorer:
    """Scores CV formatting and parse quality using heuristics from the extracted text."""

    name = "formatting"
    weight = WEIGHTS["formatting"]

    def score(self, cv: CVData, jd: JobDescription) -> DimensionScore:
        """Delegates to assess_parseability; penalises tables and low character density."""
        raw_score = assess_parseability(cv.raw_text, cv.parse_quality)

        return DimensionScore(
            name=self.name,
            weight=self.weight,
            raw_score=round(raw_score, 2),
            weighted_score=round(raw_score * self.weight, 2),
            details=MappingProxyType({
                "tables_detected": cv.parse_quality.tables_detected,
                "char_density": round(cv.parse_quality.estimated_char_density, 0),
            }),
        )
