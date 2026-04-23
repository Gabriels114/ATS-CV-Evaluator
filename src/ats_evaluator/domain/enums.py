from enum import Enum


class SeniorityLevel(str, Enum):
    INTERN = "intern"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"

    def rank(self) -> int:
        return list(SeniorityLevel).index(self)


class SkillType(str, Enum):
    HARD = "hard"
    SOFT = "soft"
    TOOL = "tool"
    LANG = "lang"


class FileKind(str, Enum):
    PDF = ".pdf"
    DOCX = ".docx"
    TXT = ".txt"
    MD = ".md"
