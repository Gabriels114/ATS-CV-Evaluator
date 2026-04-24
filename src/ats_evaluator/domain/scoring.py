from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Any

from .feedback import MissingKeyword, Suggestion


@dataclass(frozen=True, slots=True)
class DimensionScore:
    """Score for a single evaluation dimension (e.g. hard_skills, experience)."""

    name: str
    weight: float
    raw_score: float       # 0–100 within this dimension
    weighted_score: float  # raw_score * weight
    details: MappingProxyType[str, Any]


@dataclass(frozen=True, slots=True)
class ScoreReport:
    """Aggregated ATS evaluation output including scores, gaps, and suggestions."""

    total_score: float
    dimensions: tuple[DimensionScore, ...]
    missing_keywords: tuple[MissingKeyword, ...]
    suggestions: tuple[Suggestion, ...]
    cv_summary: str
    jd_summary: str
    scoring_version: str
    generated_at: datetime
