"""Tests for `clean` package."""

import sys
from typing import TYPE_CHECKING

import pytest

from invokelint._clean import clean_all
from tests.testlibraries import check_list_result

if TYPE_CHECKING:
    from invoke import Context


@pytest.mark.skipif(sys.platform == "win32", reason="Currently support only in Linux.")
def test_clean_all(context: "Context") -> None:
    """Command should success and run appropriate commands."""
    list_command_expected = [
        "rm -fr build/",
        "rm -fr dist/",
        "rm -fr .eggs/",
        "find . -name '*.egg-info' -exec rm -fr {} +",
        "find . -name '*.egg' -not -path '*/.venv/*' -exec rm -f {} +",
        "find . -name '*.pyc' -exec rm -f {} +",
        "find . -name '*.pyo' -exec rm -f {} +",
        "find . -name '*~' -exec rm -f {} +",
        "find . -name '__pycache__' -exec rm -fr {} +",
        "",
    ]
    check_list_result(clean_all(context), list_command_expected)
