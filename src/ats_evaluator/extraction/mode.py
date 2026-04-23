from enum import Enum


class ExtractionMode(str, Enum):
    LOCAL = "local"  # 100% local: regex + NLP + skills taxonomy, no API needed
    LLM = "llm"      # Claude API for higher accuracy extraction
