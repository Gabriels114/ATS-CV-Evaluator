from rich.console import Console

from ats_evaluator.reporting.formatters import score_bar, score_label, score_style
from ats_evaluator.reporting.json_export import to_dict, to_json
from ats_evaluator.reporting.terminal import render_report
from ats_evaluator.scoring.engine import score


def test_score_label():
    assert score_label(85) == "STRONG MATCH"
    assert score_label(70) == "ACCEPTABLE"
    assert score_label(50) == "AT RISK"
    assert score_label(30) == "LOW MATCH"


def test_score_bar_length():
    bar = score_bar(100, width=30)
    assert len(bar) == 30
    assert bar == "█" * 30


def test_score_bar_empty():
    bar = score_bar(0, width=30)
    assert bar == "░" * 30


def test_json_export_structure(senior_backend_cv, senior_python_jd):
    report = score(senior_backend_cv, senior_python_jd)
    data = to_dict(report)
    assert set(data.keys()) >= {"total_score", "dimensions", "missing_keywords", "suggestions"}
    assert isinstance(data["total_score"], float)


def test_json_export_is_string(senior_backend_cv, senior_python_jd):
    report = score(senior_backend_cv, senior_python_jd)
    output = to_json(report)
    assert isinstance(output, str)
    assert "total_score" in output


def test_terminal_render_no_crash(senior_backend_cv, senior_python_jd):
    report = score(senior_backend_cv, senior_python_jd)
    console = Console(file=open("/dev/null", "w"))
    render_report(report, console)  # should not raise
