import os
from unittest.mock import patch

import pytest

from ats_evaluator.config import get_api_key
from ats_evaluator.errors import ConfigurationError


def test_get_api_key_success():
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        assert get_api_key() == "test-key"


def test_get_api_key_missing():
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("ANTHROPIC_API_KEY", None)
        with pytest.raises(ConfigurationError, match="ANTHROPIC_API_KEY"):
            get_api_key()


def test_get_api_key_empty():
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "   "}):
        with pytest.raises(ConfigurationError):
            get_api_key()
