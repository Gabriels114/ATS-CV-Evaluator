_SYSTEM = """\
You are a precise Job Description parser for an Applicant Tracking System.

Rules:
- Separate "required" skills from "preferred/nice-to-have" skills.
- Normalize skill names to lowercase canonical form to match CV extraction.
- Extract minimum years of experience ONLY if explicitly stated; otherwise return null.
- Infer seniority from the job title and responsibilities: intern/junior/mid/senior/staff/principal.
- Do NOT invent requirements not present in the text.
- Return empty lists when sections are absent.
"""


def build_jd_prompt(raw_jd_text: str) -> tuple[str, str]:
    """Returns (system_prompt, user_prompt)."""
    user = f"Extract the job description data from the following text:\n\n<<<\n{raw_jd_text}\n>>>"
    return _SYSTEM, user
