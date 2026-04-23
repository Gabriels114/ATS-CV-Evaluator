from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    REQUIRED = "required"
    PREFERRED = "preferred"


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True, slots=True)
class MissingKeyword:
    keyword: str
    severity: Severity
    dimension: str


@dataclass(frozen=True, slots=True)
class Suggestion:
    dimension: str
    priority: Priority
    message: str
