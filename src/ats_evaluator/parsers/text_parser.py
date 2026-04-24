from pathlib import Path

from ..domain.cv import ParseQuality
from ..errors import UnparseableDocumentError
from .base import DocumentParser, ParsedDocument

_SUPPORTED = {".txt", ".md"}


class TextParser:
    """Reads plain-text files (.txt, .md) with UTF-8 / Latin-1 fallback decoding."""

    def can_parse(self, path: Path) -> bool:
        """Return True when the file extension is .txt or .md."""
        return path.suffix.lower() in _SUPPORTED

    def parse(self, path: Path) -> ParsedDocument:
        """Decode and return text content; raises UnparseableDocumentError for empty or undecodable files."""
        for encoding in ("utf-8", "latin-1"):
            try:
                raw_text = path.read_text(encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise UnparseableDocumentError(
                f"'{path.name}' could not be decoded as UTF-8 or Latin-1."
            )

        if not raw_text.strip():
            raise UnparseableDocumentError(f"'{path.name}' is empty.")

        quality = ParseQuality(
            page_count=1,
            has_images_only=False,
            tables_detected=False,
            estimated_char_density=float(len(raw_text)),
        )
        return ParsedDocument(raw_text=raw_text, quality=quality)


_instance: DocumentParser = TextParser()
