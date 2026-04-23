from ..domain.cv import CVData, ContactInfo, Education, WorkExperience
from ..domain.cv import ParseQuality
from .claude_client import ClaudeClient
from .prompts import CV_EXTRACTION_SCHEMA, build_cv_prompt
from .response_validator import validate_cv_response


def extract_cv(raw_text: str, quality: ParseQuality, client: ClaudeClient) -> CVData:
    system, user = build_cv_prompt(raw_text)
    raw = client.extract_structured(system, user, CV_EXTRACTION_SCHEMA)
    validated = validate_cv_response(raw)

    contact_raw = validated.get("contact") or {}
    contact = ContactInfo(
        email=contact_raw.get("email"),
        phone=contact_raw.get("phone"),
        location=contact_raw.get("location"),
        linkedin=contact_raw.get("linkedin"),
        github=contact_raw.get("github"),
    )

    experiences = tuple(
        WorkExperience(
            title=exp["title"],
            company=exp["company"],
            start_date=exp.get("start_date"),
            end_date=exp.get("end_date"),
            description=exp.get("description", ""),
            technologies=tuple(exp.get("technologies", [])),
            achievements=tuple(exp.get("achievements", [])),
            quantified_metrics=tuple(exp.get("quantified_metrics", [])),
        )
        for exp in validated.get("experiences", [])
    )

    education = tuple(
        Education(
            degree=edu.get("degree", ""),
            field=edu.get("field", ""),
            institution=edu.get("institution", ""),
            graduation_year=edu.get("graduation_year"),
        )
        for edu in validated.get("education", [])
    )

    return CVData(
        full_name=validated.get("full_name"),
        contact=contact,
        summary=validated.get("summary"),
        hard_skills=tuple(validated.get("hard_skills", [])),
        soft_skills=tuple(validated.get("soft_skills", [])),
        experiences=experiences,
        education=education,
        certifications=tuple(validated.get("certifications", [])),
        raw_text=raw_text,
        parse_quality=quality,
    )
