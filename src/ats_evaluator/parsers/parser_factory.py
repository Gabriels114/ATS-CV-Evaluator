from pathlib import Path

from ..errors import UnparseableDocumentError
from .base import DocumentParser, ParsedDocument
from .docx_parser import DocxParser
from .pdf_parser import PdfParser
from .text_parser import TextParser

_PARSERS: tuple[DocumentParser, ...] = (
    PdfParser(),
    DocxParser(),
    TextParser(),
)


def get_parser(path: Path) -> DocumentParser:
    for parser in _PARSERS:
        if parser.can_parse(path):
            return parser
    raise UnparseableDocumentError(
        f"No parser available for '{path.suffix}' files. "
        "Supported: .pdf, .docx, .txt, .md"
    )


def parse_document(path: Path) -> ParsedDocument:
    if not path.exists():
        raise FileNotFoundError(f"File not found: '{path}'")
    return get_parser(path).parse(path)
