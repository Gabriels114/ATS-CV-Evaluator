import re

from ..domain.cv import ParseQuality

_SECTION_HEADERS = re.compile(
    r"^(experience|education|skills|summary|objective|certifications|projects|"
    r"work history|employment|qualifications|profile|about)",
    re.IGNORECASE | re.MULTILINE,
)
_SUSPICIOUS_CHARS = re.compile(r"[^\x00-\x7FÀ-ɏ]")


def assess_parseability(raw_text: str, quality: ParseQuality) -> float:
    """Returns 0–100. Lower = harder for ATS to parse reliably."""
    score = 100.0

    if quality.tables_detected:
        score -= 15.0

    headers_found = len(_SECTION_HEADERS.findall(raw_text))
    if headers_found == 0:
        score -= 20.0
    elif headers_found < 3:
        score -= 10.0

    if quality.estimated_char_density < 500:
        score -= 20.0
    elif quality.estimated_char_density < 1000:
        score -= 10.0

    suspicious_ratio = len(_SUSPICIOUS_CHARS.findall(raw_text)) / max(len(raw_text), 1)
    if suspicious_ratio > 0.05:
        score -= 15.0
    elif suspicious_ratio > 0.02:
        score -= 5.0

    return max(0.0, score)
