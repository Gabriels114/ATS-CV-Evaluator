from datetime import datetime

from ..config import SCORING_VERSION
from ..domain.cv import CVData
from ..domain.job import JobDescription
from ..domain.scoring import ScoreReport
from ..feedback.generator import generate_suggestions
from ..feedback.missing_keywords import compute_missing_keywords
from .dimensions import ALL_SCORERS


def score(cv: CVData, jd: JobDescription) -> ScoreReport:
    dimensions = tuple(scorer.score(cv, jd) for scorer in ALL_SCORERS)
    total = round(sum(d.weighted_score for d in dimensions), 2)
    missing = compute_missing_keywords(cv, jd)
    suggestions = generate_suggestions(dimensions, missing)

    cv_summary = f"{cv.full_name or 'Candidate'} — {len(cv.experiences)} roles, {len(cv.hard_skills)} hard skills"
    jd_summary = f"{jd.title} ({jd.seniority.value}) — {len(jd.required_hard_skills)} required skills"

    return ScoreReport(
        total_score=total,
        dimensions=dimensions,
        missing_keywords=missing,
        suggestions=suggestions,
        cv_summary=cv_summary,
        jd_summary=jd_summary,
        scoring_version=SCORING_VERSION,
        generated_at=datetime.now(),
    )
