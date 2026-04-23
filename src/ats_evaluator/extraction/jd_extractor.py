from ..domain.enums import SeniorityLevel
from ..domain.job import JobDescription
from .claude_client import ClaudeClient
from .prompts import JD_EXTRACTION_SCHEMA, build_jd_prompt
from .response_validator import validate_jd_response


def extract_jd(raw_text: str, client: ClaudeClient) -> JobDescription:
    system, user = build_jd_prompt(raw_text)
    raw = client.extract_structured(system, user, JD_EXTRACTION_SCHEMA)
    validated = validate_jd_response(raw)

    seniority_str = validated.get("seniority", "mid").lower()
    try:
        seniority = SeniorityLevel(seniority_str)
    except ValueError:
        seniority = SeniorityLevel.MID

    return JobDescription(
        title=validated.get("title", ""),
        seniority=seniority,
        required_hard_skills=tuple(validated.get("required_hard_skills", [])),
        preferred_hard_skills=tuple(validated.get("preferred_hard_skills", [])),
        soft_skills=tuple(validated.get("soft_skills", [])),
        min_years_experience=validated.get("min_years_experience"),
        required_education=tuple(validated.get("required_education", [])),
        responsibilities=tuple(validated.get("responsibilities", [])),
        raw_text=raw_text,
    )
