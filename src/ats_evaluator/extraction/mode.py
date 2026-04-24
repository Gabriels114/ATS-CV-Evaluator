"""Defines the extraction backend mode: local regex/NLP or Claude LLM API."""

from enum import Enum


class ExtractionMode(str, Enum):
    """Selects which extraction backend to use when parsing CVs and job descriptions."""

    LOCAL = "local"  # 100% local: regex + NLP + skills taxonomy, no API needed
    LLM = "llm"      # Claude API for higher accuracy extraction
