from ..domain.cv import CVData
from ..domain.feedback import MissingKeyword, Severity
from ..domain.job import JobDescription
from ..scoring.keyword_matcher import skills_missing


def compute_missing_keywords(cv: CVData, jd: JobDescription) -> tuple[MissingKeyword, ...]:
    missing_required = skills_missing(cv.hard_skills, jd.required_hard_skills)
    missing_preferred = skills_missing(cv.hard_skills, jd.preferred_hard_skills)

    result: list[MissingKeyword] = [
        MissingKeyword(keyword=kw, severity=Severity.REQUIRED, dimension="hard_skills")
        for kw in missing_required
    ] + [
        MissingKeyword(keyword=kw, severity=Severity.PREFERRED, dimension="hard_skills")
        for kw in missing_preferred
    ]

    return tuple(result)
