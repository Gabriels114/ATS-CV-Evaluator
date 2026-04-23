from datetime import date

import pytest

from ats_evaluator.scoring.recency import recency_factor


@pytest.mark.parametrize("end_date,expected_min,expected_max", [
    (None, 1.0, 1.0),                        # current role
    (date(2024, 1, 1), 0.93, 1.0),          # ~2.3 years ago → slight decay
    (date(2021, 1, 1), 0.45, 0.55),         # ~5 years ago
    (date(2016, 1, 1), 0.28, 0.35),         # ~10 years ago
    (date(2010, 1, 1), 0.29, 0.31),         # very old → floor 0.3
])
def test_recency_factor(end_date, expected_min, expected_max):
    today = date(2026, 4, 22)
    result = recency_factor(end_date, today)
    assert expected_min <= result <= expected_max


def test_current_role_always_1():
    assert recency_factor(None, date.today()) == 1.0
