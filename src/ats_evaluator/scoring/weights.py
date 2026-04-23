from types import MappingProxyType
from typing import Final

WEIGHTS: Final = MappingProxyType({
    "hard_skills":     0.30,
    "experience":      0.25,
    "education":       0.15,
    "title_alignment": 0.10,
    "achievements":    0.10,
    "soft_skills":     0.05,
    "formatting":      0.05,
})

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Weights must sum to 1.0"
