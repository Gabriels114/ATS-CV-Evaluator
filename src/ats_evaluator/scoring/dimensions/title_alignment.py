from types import MappingProxyType

from ...domain.cv import CVData
from ...domain.enums import SeniorityLevel
from ...domain.job import JobDescription
from ...domain.scoring import DimensionScore
from ..weights import WEIGHTS

_TITLE_KEYWORDS: dict[SeniorityLevel, list[str]] = {
    SeniorityLevel.INTERN:    ["intern", "trainee", "practicante", "becario"],
    SeniorityLevel.JUNIOR:    ["junior", "jr", "entry", "associate"],
    SeniorityLevel.MID:       ["mid", "middle", "ssr", "semi-senior"],
    SeniorityLevel.SENIOR:    ["senior", "sr"],
    SeniorityLevel.STAFF:     ["staff", "lead", "tech lead"],
    SeniorityLevel.PRINCIPAL: ["principal", "distinguished", "architect", "director"],
}


def _infer_seniority(title: str) -> SeniorityLevel | None:
    tl = title.lower()
    for level, keywords in _TITLE_KEYWORDS.items():
        if any(kw in tl for kw in keywords):
            return level
    return None


class TitleAlignmentScorer:
    name = "title_alignment"
    weight = WEIGHTS["title_alignment"]

    def score(self, cv: CVData, jd: JobDescription) -> DimensionScore:
        if not cv.experiences:
            return DimensionScore(
                name=self.name, weight=self.weight,
                raw_score=50.0, weighted_score=50.0 * self.weight,
                details=MappingProxyType({"reason": "no experience to infer seniority"}),
            )

        most_recent_title = cv.experiences[0].title
        cv_seniority = _infer_seniority(most_recent_title)
        jd_seniority = jd.seniority

        if cv_seniority is None:
            raw_score = 60.0  # title present but seniority unclear
        else:
            diff = cv_seniority.rank() - jd_seniority.rank()
            if diff == 0:
                raw_score = 100.0
            elif diff == -1:
                raw_score = 70.0   # one level below
            elif diff == -2:
                raw_score = 40.0   # two levels below
            elif diff < -2:
                raw_score = 20.0
            elif diff == 1:
                raw_score = 85.0   # slightly overqualified — common, not a dealbreaker
            else:
                raw_score = 65.0   # very overqualified

        return DimensionScore(
            name=self.name,
            weight=self.weight,
            raw_score=round(raw_score, 2),
            weighted_score=round(raw_score * self.weight, 2),
            details=MappingProxyType({
                "cv_most_recent_title": most_recent_title,
                "inferred_cv_seniority": cv_seniority.value if cv_seniority else None,
                "jd_seniority": jd_seniority.value,
            }),
        )
