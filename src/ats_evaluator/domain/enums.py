from enum import Enum


class SeniorityLevel(str, Enum):
    """Ordered career-level enum used to compare JD seniority against CV titles."""

    INTERN = "intern"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"

    def rank(self) -> int:
        """Return a zero-based integer rank for numeric seniority comparisons."""
        return list(SeniorityLevel).index(self)


class SkillType(str, Enum):
    """Broad category of a skill entry in the taxonomy."""

    HARD = "hard"
    SOFT = "soft"
    TOOL = "tool"
    LANG = "lang"


class FileKind(str, Enum):
    """Supported file extensions for CV and JD uploads."""

    PDF = ".pdf"
    DOCX = ".docx"
    TXT = ".txt"
    MD = ".md"
