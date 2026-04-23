import re

_ALIASES: dict[str, str] = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "ml": "machine learning",
    "dl": "deep learning",
    "k8s": "kubernetes",
    "pg": "postgresql",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "tf": "tensorflow",
    "gcp": "google cloud",
    "aws": "amazon web services",
    "ci/cd": "ci cd",
}

_NON_ALNUM = re.compile(r"[^a-z0-9 ]")


def normalize(skill: str) -> str:
    lowered = skill.lower().strip()
    expanded = _ALIASES.get(lowered, lowered)
    return _NON_ALNUM.sub(" ", expanded).strip()


def exact_match(a: str, b: str) -> bool:
    return normalize(a) == normalize(b)


def skills_overlap(cv_skills: tuple[str, ...], jd_skills: tuple[str, ...]) -> set[str]:
    normalized_cv = {normalize(s) for s in cv_skills}
    return {s for s in jd_skills if normalize(s) in normalized_cv}


def skills_missing(cv_skills: tuple[str, ...], jd_skills: tuple[str, ...]) -> list[str]:
    normalized_cv = {normalize(s) for s in cv_skills}
    return [s for s in jd_skills if normalize(s) not in normalized_cv]
