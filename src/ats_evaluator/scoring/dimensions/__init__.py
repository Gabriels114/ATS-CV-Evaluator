from .achievements import AchievementsScorer
from .education import EducationScorer
from .experience import ExperienceScorer
from .formatting import FormattingScorer
from .hard_skills import HardSkillsScorer
from .soft_skills import SoftSkillsScorer
from .title_alignment import TitleAlignmentScorer

ALL_SCORERS = (
    HardSkillsScorer(),
    ExperienceScorer(),
    EducationScorer(),
    TitleAlignmentScorer(),
    AchievementsScorer(),
    SoftSkillsScorer(),
    FormattingScorer(),
)

__all__ = [
    "ALL_SCORERS",
    "AchievementsScorer",
    "EducationScorer",
    "ExperienceScorer",
    "FormattingScorer",
    "HardSkillsScorer",
    "SoftSkillsScorer",
    "TitleAlignmentScorer",
]
