from .claude_client import ClaudeClient
from .local import extract_cv as _local_cv, extract_jd as _local_jd
from .llm import extract_cv as _llm_cv, extract_jd as _llm_jd
from .mode import ExtractionMode
from ..errors import ConfigurationError


def extract_cv(
    raw_text: str,
    quality,
    client: ClaudeClient | None = None,
    mode: ExtractionMode = ExtractionMode.LOCAL,
):
    """Extracts structured CVData from raw text using the specified backend (local or LLM)."""
    if mode == ExtractionMode.LLM:
        if client is None:
            raise ConfigurationError("LLM mode requires a ClaudeClient instance.")
        return _llm_cv(raw_text, quality, client)
    return _local_cv(raw_text, quality)


def extract_jd(
    raw_text: str,
    client: ClaudeClient | None = None,
    mode: ExtractionMode = ExtractionMode.LOCAL,
):
    """Extracts structured JobDescription from raw text using the specified backend (local or LLM)."""
    if mode == ExtractionMode.LLM:
        if client is None:
            raise ConfigurationError("LLM mode requires a ClaudeClient instance.")
        return _llm_jd(raw_text, client)
    return _local_jd(raw_text)


__all__ = ["ClaudeClient", "ExtractionMode", "extract_cv", "extract_jd"]
