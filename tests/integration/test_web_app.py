import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from ats_evaluator.domain.cv import ParseQuality
from ats_evaluator.parsers.base import ParsedDocument
from ats_evaluator.web.app import app

client = TestClient(app, raise_server_exceptions=False)

_FAKE_DOC = ParsedDocument(
    raw_text="Jane Developer\nPython engineer",
    quality=ParseQuality(page_count=1, has_images_only=False, tables_detected=False, estimated_char_density=500.0),
)


@pytest.fixture
def mocked_extraction(senior_backend_cv, senior_python_jd):
    """Mock parse_document + extract_cv/jd so tests don't need real PDF/DOCX files."""
    with (
        patch("ats_evaluator.web.app.parse_document", return_value=_FAKE_DOC),
        patch("ats_evaluator.web.app.extract_cv", return_value=senior_backend_cv),
        patch("ats_evaluator.web.app.extract_jd", return_value=senior_python_jd),
    ):
        yield


def _cv_file(content: str = "fake pdf content") -> tuple:
    """Return a multipart file tuple using .pdf extension (passes extension whitelist)."""
    return ("cv_file", ("cv.pdf", content.encode(), "application/pdf"))


def _jd_form(text: str = "Senior Python Engineer with Docker") -> dict:
    return {"jd_text": text}


def test_index_returns_html():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "ATS CV Evaluator" in resp.text
    assert "<!DOCTYPE html>" in resp.text


def test_evaluate_local_mode_success(mocked_extraction):
    resp = client.post(
        "/evaluate",
        files=[_cv_file()],
        data={**_jd_form(), "mode": "local"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total_score" in data
    assert data["extraction_mode"] == "local"
    assert len(data["dimensions"]) == 7


def test_evaluate_returns_missing_keywords(mocked_extraction):
    resp = client.post(
        "/evaluate",
        files=[_cv_file()],
        data={**_jd_form(), "mode": "local"},
    )
    data = resp.json()
    assert "missing_keywords" in data
    assert "suggestions" in data


def test_evaluate_missing_jd_returns_422(mocked_extraction):
    resp = client.post(
        "/evaluate",
        files=[_cv_file()],
        data={"jd_text": "   ", "mode": "local"},
    )
    assert resp.status_code == 422


def test_evaluate_llm_mode_missing_key(mocked_extraction):
    resp = client.post(
        "/evaluate",
        files=[_cv_file()],
        data={**_jd_form(), "mode": "llm", "api_key": ""},
    )
    assert resp.status_code == 422
    assert "API key" in resp.json()["detail"]


def test_evaluate_llm_mode_with_key(mocked_extraction):
    resp = client.post(
        "/evaluate",
        files=[_cv_file()],
        data={**_jd_form(), "mode": "llm", "api_key": "sk-ant-test-key"},
    )
    assert resp.status_code == 200
    assert resp.json()["extraction_mode"] == "llm"


def test_evaluate_invalid_mode(mocked_extraction):
    resp = client.post(
        "/evaluate",
        files=[_cv_file()],
        data={**_jd_form(), "mode": "superllm"},
    )
    assert resp.status_code == 422


def test_evaluate_rejected_cv_extension():
    """Extension whitelist rejects non-PDF/DOCX files with HTTP 422."""
    resp = client.post(
        "/evaluate",
        files=[("cv_file", ("cv.txt", b"some text", "text/plain"))],
        data=_jd_form(),
    )
    assert resp.status_code == 422
    assert ".txt" in resp.json()["detail"]


def test_evaluate_malformed_cv():
    with patch("ats_evaluator.web.app.parse_document", side_effect=Exception("bad file")):
        resp = client.post(
            "/evaluate",
            files=[_cv_file()],
            data={**_jd_form(), "mode": "local"},
        )
    assert resp.status_code in (422, 500)
