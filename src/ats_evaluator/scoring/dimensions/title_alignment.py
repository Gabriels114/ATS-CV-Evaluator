from types import MappingProxyType
from typing import Final

from ...domain.cv import CVData
from ...domain.enums import SeniorityLevel
from ...domain.job import JobDescription
from ...domain.scoring import DimensionScore
from ..weights import WEIGHTS

_TITLE_SYNONYMS: Final[dict[SeniorityLevel, list[str]]] = {
    SeniorityLevel.INTERN: [
        "intern", "internship", "trainee", "practicante", "becario",
        "student developer", "co-op", "apprentice",
    ],
    SeniorityLevel.JUNIOR: [
        "junior", "jr", "jr.", "entry level", "entry-level", "associate",
        "associate engineer", "graduate", "new grad", "early career",
        "software developer i", "engineer i",
    ],
    SeniorityLevel.MID: [
        "mid", "mid-level", "mid level", "ssr", "semi-senior",
        "intermediate", "software developer ii", "engineer ii",
        "software engineer",
        # "developer" intentionally excluded: too generic, causes false MID on "Junior Developer"
    ],
    SeniorityLevel.SENIOR: [
        "senior", "sr", "sr.", "senior engineer", "senior developer",
        "software developer iii", "engineer iii", "experienced",
    ],
    SeniorityLevel.STAFF: [
        "staff", "tech lead", "technical lead", "lead engineer",
        "lead developer", "team lead", "engineering lead",
        "senior staff", "staff software engineer",
    ],
    SeniorityLevel.PRINCIPAL: [
        "principal", "distinguished", "architect", "software architect",
        "solutions architect", "vp of engineering", "director of engineering",
        "head of engineering", "chief engineer", "fellow", "engineering fellow",
        "vp", "director", "head of",
    ],
}


def _infer_seniority(title: str) -> SeniorityLevel | None:
    """
    Infers seniority from a job title using the synonym map.
    Checks PRINCIPAL first (highest priority) down to INTERN.
    Returns None if no match found.
    """
    tl = title.lower()
    for level in [
        SeniorityLevel.PRINCIPAL,
        SeniorityLevel.STAFF,
        SeniorityLevel.SENIOR,
        SeniorityLevel.MID,
        SeniorityLevel.JUNIOR,
        SeniorityLevel.INTERN,
    ]:
        synonyms = _TITLE_SYNONYMS.get(level, [])
        if any(syn in tl for syn in synonyms):
            return level
    return None


class TitleAlignmentScorer:
    """Scores alignment between the candidate's most recent title seniority and the JD seniority."""

    name = "title_alignment"
    weight = WEIGHTS["title_alignment"]

    def score(self, cv: CVData, jd: JobDescription) -> DimensionScore:
        """Rank difference between inferred CV seniority and JD seniority drives the score."""
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
