"""Tests for `style` package."""

from typing import TYPE_CHECKING

import pytest
from invoke.exceptions import Exit

from invokelint.style import fmt
from tests.testlibraries import check_list_result

if TYPE_CHECKING:
    from invoke import Context

PYTHON_DIR = "invokelint setup.py tasks.py tests"

LIST_COMMAND_EXPECTED_STYLE_COMMON = [
    f"docformatter --recursive --in-place {PYTHON_DIR}",
]
LIST_COMMAND_EXPECTED_STYLE_WITHOUT_RUFF = [
    *LIST_COMMAND_EXPECTED_STYLE_COMMON,
    f"autoflake --recursive --in-place {PYTHON_DIR}",
    f"isort {PYTHON_DIR}",
    f"black {PYTHON_DIR}",
]
LIST_COMMAND_EXPECTED_STYLE_WITHOUT_RUFF_BY_RUFF = [
    *LIST_COMMAND_EXPECTED_STYLE_COMMON,
    f"ruff format --diff {PYTHON_DIR}",
    f"ruff format {PYTHON_DIR}",
]
LIST_COMMAND_EXPECTED_STYLE_BY_RUFF = [
    *LIST_COMMAND_EXPECTED_STYLE_WITHOUT_RUFF_BY_RUFF,
    f"ruff check --show-fixes {PYTHON_DIR}",
    f"ruff check --fix --show-fixes {PYTHON_DIR}",
]
LIST_COMMAND_EXPECTED_STYLE_NO_RUFF = [
    *LIST_COMMAND_EXPECTED_STYLE_WITHOUT_RUFF,
    f"ruff check --show-fixes {PYTHON_DIR}",
    f"ruff check --fix --show-fixes {PYTHON_DIR}",
]
LIST_COMMAND_EXPECTED_STYLE_CHECK_COMMON = [
    f"docformatter --recursive --check {PYTHON_DIR}",
]
LIST_COMMAND_EXPECTED_STYLE_CHECK_NO_RUFF = [
    *LIST_COMMAND_EXPECTED_STYLE_CHECK_COMMON,
    f"autoflake --recursive --check {PYTHON_DIR}",
    f"isort --check-only --diff {PYTHON_DIR}",
    f"black --check --diff {PYTHON_DIR}",
    f"ruff check --show-fixes {PYTHON_DIR}",
]
LIST_COMMAND_EXPECTED_STYLE_CHECK_BY_RUFF = [
    *LIST_COMMAND_EXPECTED_STYLE_CHECK_COMMON,
    f"ruff format --diff {PYTHON_DIR}",
    f"ruff check --show-fixes {PYTHON_DIR}",
]
LIST_COMMAND_EXPECTED_STYLE_RUFF = [
    *LIST_COMMAND_EXPECTED_STYLE_COMMON,
    f"ruff format --diff {PYTHON_DIR}",
    f"ruff format {PYTHON_DIR}",
]


def test_style(context: "Context") -> None:
    """Command should success and run appropriate commands."""
    check_list_result(fmt(context), LIST_COMMAND_EXPECTED_STYLE_BY_RUFF)


def test_style_by_ruff(context: "Context") -> None:
    """Command should success and run appropriate commands."""
    check_list_result(fmt(context, by_ruff=True), LIST_COMMAND_EXPECTED_STYLE_BY_RUFF)


def test_style_no_ruff(context: "Context") -> None:
    """Command should success and run appropriate commands."""
    check_list_result(fmt(context, no_ruff=True), LIST_COMMAND_EXPECTED_STYLE_NO_RUFF)


def test_style_check(context: "Context") -> None:
    """Command should success and run appropriate commands."""
    check_list_result(fmt(context, check=True), LIST_COMMAND_EXPECTED_STYLE_CHECK_BY_RUFF)


def test_style_check_by_ruff(context: "Context") -> None:
    """Command should success and run appropriate commands."""
    check_list_result(fmt(context, check=True, by_ruff=True), LIST_COMMAND_EXPECTED_STYLE_CHECK_BY_RUFF)


def test_style_check_no_ruff(context: "Context") -> None:
    """Command should success and run appropriate commands."""
    check_list_result(fmt(context, check=True, no_ruff=True), LIST_COMMAND_EXPECTED_STYLE_CHECK_NO_RUFF)


def test_style_ruff(context: "Context") -> None:
    """Command should success and run appropriate commands."""
    check_list_result(fmt(context, ruff=True), LIST_COMMAND_EXPECTED_STYLE_RUFF)


def test_style_ruff_by_ruff_no_ruff(context: "Context") -> None:
    """Command should success and run appropriate commands."""
    with pytest.raises(Exit) as exc_info:
        fmt(context, ruff=True, by_ruff=True, no_ruff=True)
    assert str(exc_info.value) == "Cannot use both '--by-ruff' and '--no-ruff' options together."
