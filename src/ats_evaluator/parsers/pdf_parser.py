from pathlib import Path

import pdfplumber

from ..domain.cv import ParseQuality
from ..errors import UnparseableDocumentError
from .base import DocumentParser, ParsedDocument


class PdfParser:
    """Extracts text and quality metadata from PDF files using pdfplumber."""

    def can_parse(self, path: Path) -> bool:
        """Return True when the file has a .pdf extension."""
        return path.suffix.lower() == ".pdf"

    def parse(self, path: Path) -> ParsedDocument:
        """Extract raw text and parse quality from a PDF; raises UnparseableDocumentError on failure."""
        pages_text: list[str] = []
        page_count = 0
        tables_detected = False

        try:
            with pdfplumber.open(path) as pdf:
                page_count = len(pdf.pages)
                for page in pdf.pages:
                    if page.extract_tables():
                        tables_detected = True
                    text = page.extract_text() or ""
                    pages_text.append(text)
        except Exception as exc:
            raise UnparseableDocumentError(f"Failed to open PDF '{path.name}': {exc}") from exc

        raw_text = "\n\n".join(p for p in pages_text if p.strip())

        if not raw_text.strip():
            raise UnparseableDocumentError(
                f"'{path.name}' contains no extractable text. "
                "It may be a scanned image-only PDF. Run OCR first (e.g., ocrmypdf)."
            )

        char_density = len(raw_text) / max(page_count, 1)
        quality = ParseQuality(
            page_count=page_count,
            has_images_only=False,
            tables_detected=tables_detected,
            estimated_char_density=char_density,
        )
        return ParsedDocument(raw_text=raw_text, quality=quality)


_instance: DocumentParser = PdfParser()
