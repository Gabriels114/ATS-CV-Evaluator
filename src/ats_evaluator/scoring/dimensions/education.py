from types import MappingProxyType

from ...domain.cv import CVData
from ...domain.job import JobDescription
from ...domain.scoring import DimensionScore
from ..weights import WEIGHTS

_DEGREE_RANK: dict[str, int] = {
    "phd": 5, "doctorate": 5, "doctor": 5,
    "master": 4, "msc": 4, "mba": 4, "ms": 4,
    "bachelor": 3, "bsc": 3, "bs": 3, "licenciatura": 3, "ingenieria": 3,
    "associate": 2,
    "high school": 1, "diploma": 1,
}


def _degree_level(degree: str) -> int:
    """Map a degree string to a numeric rank (0 = unrecognised, 5 = doctorate)."""
    dl = degree.lower()
    for key, rank in _DEGREE_RANK.items():
        if key in dl:
            return rank
    return 0


class EducationScorer:
    """Scores education level and field alignment against JD requirements."""

    name = "education"
    weight = WEIGHTS["education"]

    def score(self, cv: CVData, jd: JobDescription) -> DimensionScore:
        """Level score (70%) + field-match bonus (30%) when JD specifies requirements."""
        if not cv.education:
            return DimensionScore(
                name=self.name, weight=self.weight,
                raw_score=0.0, weighted_score=0.0,
                details=MappingProxyType({"reason": "no education found in cv"}),
            )

        highest_level = max(_degree_level(edu.degree) for edu in cv.education)

        required_levels = [
            _degree_level(req)
            for req in jd.required_education
            if _degree_level(req) > 0
        ]
        required_level = max(required_levels) if required_levels else 3  # default: bachelor

        if highest_level >= required_level:
            level_score = 100.0
        elif highest_level == required_level - 1:
            level_score = 70.0
        elif highest_level == 0:
            level_score = 20.0
        else:
            level_score = 40.0

        # Field match bonus
        field_match = False
        if jd.required_education:
            jd_fields = " ".join(jd.required_education).lower()
            for edu in cv.education:
                if any(word in jd_fields for word in edu.field.lower().split()):
                    field_match = True
                    break

        raw_score = level_score if not jd.required_education else (
            level_score * 0.7 + (30.0 if field_match else 0.0)
        )

        return DimensionScore(
            name=self.name,
            weight=self.weight,
            raw_score=round(raw_score, 2),
            weighted_score=round(raw_score * self.weight, 2),
            details=MappingProxyType({
                "highest_degree_level": highest_level,
                "required_level": required_level,
                "field_match": field_match,
            }),
        )
