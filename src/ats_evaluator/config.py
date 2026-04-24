import os
from pathlib import Path
from typing import Final

from .errors import ConfigurationError

MODEL_ID: Final[str] = "claude-sonnet-4-6"
SCORING_VERSION: Final[str] = "1.0"

CLAUDE_TEMPERATURE: Final[float] = 0.0
CLAUDE_MAX_TOKENS: Final[int] = 4096
CLAUDE_MAX_RETRIES: Final[int] = 2
CLAUDE_TIMEOUT_SECONDS: Final[int] = 60

CACHE_DIR: Final[Path] = Path.home() / ".cache" / "ats" / "extractions"

PROMPT_VERSION: Final[str] = "1.0"


def get_api_key() -> str:
    """Read ANTHROPIC_API_KEY from the environment; raise ConfigurationError when absent."""
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise ConfigurationError(
            "ANTHROPIC_API_KEY is not set. "
            "Export it via: export ANTHROPIC_API_KEY=your_key_here"
        )
    return key
