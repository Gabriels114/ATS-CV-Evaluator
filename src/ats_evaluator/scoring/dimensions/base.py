from typing import Protocol

from ...domain.cv import CVData
from ...domain.job import JobDescription
from ...domain.scoring import DimensionScore


class DimensionScorer(Protocol):
    name: str
    weight: float

    def score(self, cv: CVData, jd: JobDescription) -> DimensionScore: ...
