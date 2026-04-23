import dataclasses
from datetime import date

import pytest

from ats_evaluator.domain.cv import CVData, ContactInfo, Education, ParseQuality, WorkExperience
from ats_evaluator.domain.enums import SeniorityLevel
from ats_evaluator.domain.job import JobDescription


def test_work_experience_is_frozen():
    exp = WorkExperience(
        title="Engineer", company="ACME", start_date=date(2020, 1, 1),
        end_date=None, description="desc",
        technologies=("python",), achievements=(), quantified_metrics=(),
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        exp.title = "Manager"  # type: ignore


def test_cv_data_is_frozen(senior_backend_cv):
    with pytest.raises(dataclasses.FrozenInstanceError):
        senior_backend_cv.full_name = "Hacker"  # type: ignore


def test_job_description_is_frozen(senior_python_jd):
    with pytest.raises(dataclasses.FrozenInstanceError):
        senior_python_jd.title = "Hacked"  # type: ignore


def test_education_is_frozen():
    edu = Education(degree="BSc", field="CS", institution="UNAM", graduation_year=2020)
    with pytest.raises(dataclasses.FrozenInstanceError):
        edu.degree = "PhD"  # type: ignore
