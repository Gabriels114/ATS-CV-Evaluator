import io
import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from ats_evaluator.web.app import app

client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mocked_extraction(senior_backend_cv, senior_python_jd):
    with (
        patch("ats_evaluator.web.app.extract_cv", return_value=senior_backend_cv),
        patch("ats_evaluator.web.app.extract_jd", return_value=senior_python_jd),
    ):
        yield


def _cv_file(content: str = "Jane Developer\nPython engineer") -> tuple:
    return ("cv_file", ("cv.txt", content.encode(), "text/plain"))


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


def test_evaluate_missing_jd_returns_422():
    resp = client.post(
        "/evaluate",
        files=[_cv_file()],
        data={"jd_text": "   ", "mode": "local"},
    )
    assert resp.status_code == 422


def test_evaluate_llm_mode_missing_key():
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


def test_evaluate_invalid_mode():
    resp = client.post(
        "/evaluate",
        files=[_cv_file()],
        data={**_jd_form(), "mode": "superllm"},
    )
    assert resp.status_code == 422


def test_evaluate_malformed_cv(mocked_extraction):
    with patch("ats_evaluator.web.app.parse_document", side_effect=Exception("bad file")):
        resp = client.post(
            "/evaluate",
            files=[_cv_file()],
            data={**_jd_form(), "mode": "local"},
        )
    assert resp.status_code in (422, 500)
