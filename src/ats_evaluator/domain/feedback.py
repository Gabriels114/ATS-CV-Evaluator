from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    """Whether a missing skill is required or merely preferred by the JD."""

    REQUIRED = "required"
    PREFERRED = "preferred"


class Priority(str, Enum):
    """Urgency level used to order actionable suggestions for the candidate."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True, slots=True)
class MissingKeyword:
    """A skill or keyword present in the JD but absent from the CV."""

    keyword: str
    severity: Severity
    dimension: str


@dataclass(frozen=True, slots=True)
class Suggestion:
    """Actionable improvement recommendation for a specific scoring dimension."""

    dimension: str
    priority: Priority
    message: str
