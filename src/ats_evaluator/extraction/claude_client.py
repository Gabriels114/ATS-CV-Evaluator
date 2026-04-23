import hashlib
import json
import time
from pathlib import Path
from typing import Any

import anthropic

from ..config import (
    CACHE_DIR,
    CLAUDE_MAX_RETRIES,
    CLAUDE_MAX_TOKENS,
    CLAUDE_TEMPERATURE,
    CLAUDE_TIMEOUT_SECONDS,
    MODEL_ID,
    PROMPT_VERSION,
)
from ..errors import ExtractionError, InvalidExtractionError


class ClaudeClient:
    def __init__(self, api_key: str, model: str = MODEL_ID, use_cache: bool = True) -> None:
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model
        self._use_cache = use_cache

    def extract_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        tool_schema: dict[str, Any],
    ) -> dict[str, Any]:
        cache_key = self._cache_key(system_prompt, user_prompt, tool_schema)
        if self._use_cache:
            cached = self._load_cache(cache_key)
            if cached is not None:
                return cached

        result = self._call_with_retries(system_prompt, user_prompt, tool_schema)

        if self._use_cache:
            self._save_cache(cache_key, result)

        return result

    def _call_with_retries(
        self,
        system_prompt: str,
        user_prompt: str,
        tool_schema: dict[str, Any],
        validation_error: str | None = None,
    ) -> dict[str, Any]:
        prompt = user_prompt
        if validation_error:
            prompt = (
                f"{user_prompt}\n\n"
                f"Your previous response failed validation: {validation_error}\n"
                "Return corrected data using the tool."
            )

        for attempt in range(CLAUDE_MAX_RETRIES):
            try:
                response = self._client.messages.create(
                    model=self._model,
                    max_tokens=CLAUDE_MAX_TOKENS,
                    temperature=CLAUDE_TEMPERATURE,
                    system=system_prompt,
                    tools=[tool_schema],
                    tool_choice={"type": "tool", "name": tool_schema["name"]},
                    messages=[{"role": "user", "content": prompt}],
                    timeout=CLAUDE_TIMEOUT_SECONDS,
                )
            except anthropic.RateLimitError:
                if attempt < CLAUDE_MAX_RETRIES - 1:
                    time.sleep(2 ** attempt * 5)
                    continue
                raise ExtractionError("Claude API rate limit exceeded. Try again later.")
            except anthropic.APIConnectionError as exc:
                raise ExtractionError(f"Network error connecting to Claude: {exc}") from exc
            except anthropic.APIError as exc:
                raise ExtractionError(f"Claude API error: {exc}") from exc

            tool_block = next(
                (b for b in response.content if b.type == "tool_use"),
                None,
            )
            if tool_block is None:
                raise InvalidExtractionError(
                    f"Claude did not call the expected tool '{tool_schema['name']}'."
                )

            return tool_block.input  # type: ignore[no-any-return]

        raise InvalidExtractionError(
            f"Claude failed to return valid output after {CLAUDE_MAX_RETRIES} attempts."
        )

    def _cache_key(self, system: str, user: str, schema: dict[str, Any]) -> str:
        payload = json.dumps([system, user, schema, PROMPT_VERSION], sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def _load_cache(self, key: str) -> dict[str, Any] | None:
        path = CACHE_DIR / f"{key}.json"
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                return None
        return None

    def _save_cache(self, key: str, data: dict[str, Any]) -> None:
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            (CACHE_DIR / f"{key}.json").write_text(json.dumps(data, ensure_ascii=False))
        except Exception:
            pass  # caching is best-effort
