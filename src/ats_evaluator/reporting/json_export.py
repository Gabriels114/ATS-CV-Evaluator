import json
from typing import Any

from ..domain.scoring import ScoreReport


def to_dict(report: ScoreReport) -> dict[str, Any]:
    return {
        "total_score": report.total_score,
        "scoring_version": report.scoring_version,
        "generated_at": report.generated_at.isoformat(),
        "cv_summary": report.cv_summary,
        "jd_summary": report.jd_summary,
        "dimensions": [
            {
                "name": d.name,
                "weight": d.weight,
                "raw_score": d.raw_score,
                "weighted_score": d.weighted_score,
                "details": dict(d.details),
            }
            for d in report.dimensions
        ],
        "missing_keywords": [
            {"keyword": m.keyword, "severity": m.severity.value, "dimension": m.dimension}
            for m in report.missing_keywords
        ],
        "suggestions": [
            {"dimension": s.dimension, "priority": s.priority.value, "message": s.message}
            for s in report.suggestions
        ],
    }


def to_json(report: ScoreReport) -> str:
    return json.dumps(to_dict(report), ensure_ascii=False, indent=2, default=str)
