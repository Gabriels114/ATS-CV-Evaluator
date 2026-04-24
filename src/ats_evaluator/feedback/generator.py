from __future__ import annotations

from typing import TYPE_CHECKING

from ..domain.feedback import MissingKeyword, Priority, Severity, Suggestion
from ..domain.scoring import DimensionScore

if TYPE_CHECKING:
    from ..domain.cv import ContactInfo

_THRESHOLDS = {"high": 60.0, "medium": 75.0}


def _priority_for_score(raw_score: float) -> Priority:
    if raw_score < _THRESHOLDS["high"]:
        return Priority.HIGH
    if raw_score < _THRESHOLDS["medium"]:
        return Priority.MEDIUM
    return Priority.LOW


_MESSAGES: dict[str, dict[str, str]] = {
    "hard_skills": {
        Priority.HIGH: "Add explicit experience with the required hard skills listed in the JD. Cover each must-have technology in at least one role.",
        Priority.MEDIUM: "Mention more of the preferred skills; even brief familiarity helps.",
        Priority.LOW: "Hard skills match is strong. Consider adding preferred skills as a bonus.",
    },
    "experience": {
        Priority.HIGH: "Your weighted relevant experience is below the minimum. Highlight transferable roles more explicitly.",
        Priority.MEDIUM: "Emphasize recent roles most relevant to this JD; move them to the top.",
        Priority.LOW: "Experience section is solid.",
    },
    "education": {
        Priority.HIGH: "The JD requires a higher degree. Consider adding relevant certifications or coursework to partially compensate.",
        Priority.MEDIUM: "Ensure your field of study is clearly stated to improve field-match scoring.",
        Priority.LOW: "Education meets or exceeds requirements.",
    },
    "title_alignment": {
        Priority.HIGH: "Your most recent title is significantly below the JD seniority. Reframe your responsibilities to reflect the seniority level.",
        Priority.MEDIUM: "Consider adding a professional summary that clarifies your actual seniority.",
        Priority.LOW: "Title alignment is good.",
    },
    "achievements": {
        Priority.HIGH: "Add quantified metrics to at least 3–5 bullet points: dollar impact ($X), percentages (Y%), or scale (Z users/requests).",
        Priority.MEDIUM: "You have some metrics but aim for one per role. Numbers make ATS and recruiters pay attention.",
        Priority.LOW: "Good use of quantified achievements.",
    },
    "soft_skills": {
        Priority.HIGH: "Incorporate soft skills mentioned in the JD into your summary and bullet points.",
        Priority.MEDIUM: "Mirror some of the JD's soft skill language in your summary.",
        Priority.LOW: "Soft skills are well represented.",
    },
    "formatting": {
        Priority.HIGH: "Reformat your CV: use standard sections (Experience, Education, Skills), avoid tables/columns/text boxes. ATS parsers misread them.",
        Priority.MEDIUM: "Simplify formatting — reduce table usage and ensure section headers are plain text.",
        Priority.LOW: "CV formatting is ATS-friendly.",
    },
}


def _contact_suggestions(contact: ContactInfo | None) -> list[Suggestion]:
    """Returns HIGH/MEDIUM/LOW suggestions for missing contact fields."""
    if contact is None:
        return []

    suggestions: list[Suggestion] = []

    if contact.email is None:
        suggestions.append(Suggestion(
            dimension="contact",
            priority=Priority.HIGH,
            message="Add your email address — ATS systems parse contact info first and may discard CVs without it.",
        ))

    if contact.linkedin is None:
        suggestions.append(Suggestion(
            dimension="contact",
            priority=Priority.MEDIUM,
            message="Add your LinkedIn URL — most ATS systems use it for profile verification.",
        ))

    if contact.phone is None:
        suggestions.append(Suggestion(
            dimension="contact",
            priority=Priority.LOW,
            message="Consider adding a phone number for recruiter outreach.",
        ))

    return suggestions


def generate_suggestions(
    dimensions: tuple[DimensionScore, ...],
    missing: tuple[MissingKeyword, ...],
    contact: ContactInfo | None = None,
) -> tuple[Suggestion, ...]:
    suggestions: list[Suggestion] = []

    for dim in sorted(dimensions, key=lambda d: d.raw_score):
        priority = _priority_for_score(dim.raw_score)
        messages = _MESSAGES.get(dim.name, {})
        message = messages.get(priority, "")
        if message:
            suggestions.append(Suggestion(dimension=dim.name, priority=priority, message=message))

    required_missing = [m for m in missing if m.severity == Severity.REQUIRED]
    if required_missing:
        kws = ", ".join(m.keyword for m in required_missing[:5])
        suggestions.append(Suggestion(
            dimension="hard_skills",
            priority=Priority.HIGH,
            message=f"Missing required skills: {kws}. Add concrete experience or projects with these technologies.",
        ))

    suggestions.extend(_contact_suggestions(contact))

    return tuple(suggestions)
