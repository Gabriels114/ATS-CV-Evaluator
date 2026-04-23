import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from ats_evaluator.cli import app

runner = CliRunner()


@pytest.fixture
def cv_file(tmp_path: Path) -> Path:
    f = tmp_path / "cv.txt"
    f.write_text("Jane Developer\nSenior Python Engineer at ACME")
    return f


@pytest.fixture
def jd_file(tmp_path: Path) -> Path:
    f = tmp_path / "jd.txt"
    f.write_text("We need a Senior Python Engineer with 5+ years experience.")
    return f


@pytest.fixture
def mock_client_and_data(senior_backend_cv, senior_python_jd):
    with (
        patch("ats_evaluator.cli.get_api_key", return_value="fake-key"),
        patch("ats_evaluator.cli.ClaudeClient") as MockClient,
        patch("ats_evaluator.cli.extract_cv", return_value=senior_backend_cv),
        patch("ats_evaluator.cli.extract_jd", return_value=senior_python_jd),
    ):
        yield MockClient


def test_evaluate_succeeds(cv_file, jd_file, mock_client_and_data):
    result = runner.invoke(app, ["evaluate", str(cv_file), str(jd_file)])
    assert result.exit_code == 0
    assert "ATS CV Evaluator" in result.output


def test_evaluate_exports_json(cv_file, jd_file, mock_client_and_data, tmp_path):
    json_path = tmp_path / "report.json"
    result = runner.invoke(app, ["evaluate", str(cv_file), str(jd_file), "--json", str(json_path)])
    assert result.exit_code == 0
    assert json_path.exists()
    data = json.loads(json_path.read_text())
    assert "total_score" in data
    assert len(data["dimensions"]) == 7


def test_missing_cv_file(jd_file, mock_client_and_data, tmp_path):
    result = runner.invoke(app, ["evaluate", str(tmp_path / "nonexistent.pdf"), str(jd_file)])
    assert result.exit_code != 0


def test_missing_api_key_llm_mode(cv_file, jd_file):
    from ats_evaluator.errors import ConfigurationError
    with patch("ats_evaluator.cli.get_api_key", side_effect=ConfigurationError("No key")):
        result = runner.invoke(app, ["evaluate", str(cv_file), str(jd_file), "--mode", "llm"])
        assert result.exit_code == 3


def test_local_mode_no_api_key_needed(cv_file, jd_file, mock_client_and_data):
    # local mode should succeed even without patching get_api_key
    result = runner.invoke(app, ["evaluate", str(cv_file), str(jd_file), "--mode", "local"])
    assert result.exit_code == 0


def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output
