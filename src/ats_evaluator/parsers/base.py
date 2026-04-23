from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..domain.cv import ParseQuality


@dataclass(frozen=True, slots=True)
class ParsedDocument:
    raw_text: str
    quality: ParseQuality


class DocumentParser(Protocol):
    def can_parse(self, path: Path) -> bool: ...
    def parse(self, path: Path) -> ParsedDocument: ...
