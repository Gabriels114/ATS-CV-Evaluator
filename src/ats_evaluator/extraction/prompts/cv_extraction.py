_SYSTEM = """\
You are a precise CV/resume parser for an Applicant Tracking System.

Rules:
- Extract ONLY information explicitly stated in the CV. Do NOT infer or fabricate.
- Normalize skill names to lowercase canonical form: "python" not "Python", "postgresql" not "Postgres".
- For each work experience, extract ALL numeric achievements separately (dollar amounts, percentages, scale numbers, time savings) into quantified_metrics.
- Classify skills as hard (tech, tools, programming languages) or soft (communication, leadership, teamwork).
- For dates, use "YYYY-MM" or "YYYY"; use null for current role's end_date.
- If a field is absent, return null or an empty list — never fabricate data.
- Deduplicate skills: each skill appears only once in hard_skills or soft_skills.
"""


def build_cv_prompt(raw_cv_text: str) -> tuple[str, str]:
    """Returns (system_prompt, user_prompt)."""
    user = f"Extract the CV data from the following text:\n\n<<<\n{raw_cv_text}\n>>>"
    return _SYSTEM, user
