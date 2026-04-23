from pathlib import Path

import pytest

from ats_evaluator.errors import UnparseableDocumentError
from ats_evaluator.parsers.text_parser import TextParser
from ats_evaluator.parsers.parser_factory import get_parser, parse_document
from ats_evaluator.parsers.format_quality import assess_parseability
from ats_evaluator.domain.cv import ParseQuality


def test_text_parser_utf8(tmp_path):
    f = tmp_path / "jd.txt"
    f.write_text("We need a Python engineer with 5 years of experience.", encoding="utf-8")
    parser = TextParser()
    doc = parser.parse(f)
    assert "Python" in doc.raw_text
    assert doc.quality.page_count == 1


def test_text_parser_empty_raises(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_text("   ", encoding="utf-8")
    parser = TextParser()
    with pytest.raises(UnparseableDocumentError):
        parser.parse(f)


def test_text_parser_can_parse_txt(tmp_path):
    parser = TextParser()
    assert parser.can_parse(Path("resume.txt"))
    assert parser.can_parse(Path("jd.md"))
    assert not parser.can_parse(Path("cv.pdf"))


def test_parser_factory_unsupported():
    with pytest.raises(UnparseableDocumentError, match="No parser"):
        get_parser(Path("cv.xlsx"))


def test_parse_document_missing_file():
    with pytest.raises(FileNotFoundError):
        parse_document(Path("/nonexistent/path/cv.txt"))


def test_assess_parseability_good():
    quality = ParseQuality(
        page_count=2, has_images_only=False, tables_detected=False, estimated_char_density=2000.0
    )
    raw = "Experience\nEducation\nSkills\n" + "a" * 500
    score = assess_parseability(raw, quality)
    assert score >= 70.0


def test_assess_parseability_with_tables():
    quality = ParseQuality(
        page_count=1, has_images_only=False, tables_detected=True, estimated_char_density=800.0
    )
    raw = "Experience\nEducation\n" + "a" * 200
    score = assess_parseability(raw, quality)
    # Tables reduce score
    assert score < 90.0


def test_assess_parseability_no_sections():
    quality = ParseQuality(
        page_count=1, has_images_only=False, tables_detected=False, estimated_char_density=300.0
    )
    raw = "just some text with no sections at all"
    score = assess_parseability(raw, quality)
    assert score < 70.0
