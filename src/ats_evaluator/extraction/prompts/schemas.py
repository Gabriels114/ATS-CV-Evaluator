from typing import Any

CV_EXTRACTION_SCHEMA: dict[str, Any] = {
    "name": "extract_cv",
    "description": "Extract structured data from a CV/resume text.",
    "input_schema": {
        "type": "object",
        "properties": {
            "full_name": {"type": ["string", "null"]},
            "contact": {
                "type": "object",
                "properties": {
                    "email":    {"type": ["string", "null"]},
                    "phone":    {"type": ["string", "null"]},
                    "location": {"type": ["string", "null"]},
                    "linkedin": {"type": ["string", "null"]},
                    "github":   {"type": ["string", "null"]},
                },
                "required": ["email", "phone", "location", "linkedin", "github"],
            },
            "summary": {"type": ["string", "null"]},
            "hard_skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Technologies, programming languages, tools — lowercase canonical names.",
            },
            "soft_skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Communication, leadership, teamwork — lowercase.",
            },
            "experiences": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title":               {"type": "string"},
                        "company":             {"type": "string"},
                        "start_date":          {"type": ["string", "null"], "description": "YYYY-MM or YYYY"},
                        "end_date":            {"type": ["string", "null"], "description": "YYYY-MM, YYYY, or null if current"},
                        "description":         {"type": "string"},
                        "technologies":        {"type": "array", "items": {"type": "string"}},
                        "achievements":        {"type": "array", "items": {"type": "string"}},
                        "quantified_metrics":  {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["title", "company", "start_date", "end_date",
                                 "description", "technologies", "achievements", "quantified_metrics"],
                },
            },
            "education": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "degree":           {"type": "string"},
                        "field":            {"type": "string"},
                        "institution":      {"type": "string"},
                        "graduation_year":  {"type": ["integer", "null"]},
                    },
                    "required": ["degree", "field", "institution", "graduation_year"],
                },
            },
            "certifications": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "full_name", "contact", "summary", "hard_skills", "soft_skills",
            "experiences", "education", "certifications",
        ],
        "additionalProperties": False,
    },
}

JD_EXTRACTION_SCHEMA: dict[str, Any] = {
    "name": "extract_job_description",
    "description": "Extract structured requirements from a job description.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "seniority": {
                "type": "string",
                "enum": ["intern", "junior", "mid", "senior", "staff", "principal"],
            },
            "required_hard_skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Must-have technical skills — lowercase canonical.",
            },
            "preferred_hard_skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Nice-to-have technical skills — lowercase canonical.",
            },
            "soft_skills": {"type": "array", "items": {"type": "string"}},
            "min_years_experience": {
                "type": ["integer", "null"],
                "description": "Only if explicitly stated in the JD; else null.",
            },
            "required_education": {
                "type": "array",
                "items": {"type": "string"},
                "description": "e.g. ['bachelor', 'computer science']",
            },
            "responsibilities": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "title", "seniority", "required_hard_skills", "preferred_hard_skills",
            "soft_skills", "min_years_experience", "required_education", "responsibilities",
        ],
        "additionalProperties": False,
    },
}
