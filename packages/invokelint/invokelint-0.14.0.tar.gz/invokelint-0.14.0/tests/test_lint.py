"""Tests for `lint` package."""

import platform
import sys
from typing import TYPE_CHECKING

import pytest

from invokelint.lint import bandit
from invokelint.lint import cohesion
from invokelint.lint import deep
from invokelint.lint import dodgy
from invokelint.lint import fast
from invokelint.lint import flake8
from invokelint.lint import mypy
from invokelint.lint import pydocstyle
from invokelint.lint import pylint
from invokelint.lint import radon
from invokelint.lint import radon_cc
from invokelint.lint import radon_mi
from invokelint.lint import ruff_task
from invokelint.lint import semgrep
from invokelint.lint import xenon
from tests.test_style import LIST_COMMAND_EXPECTED_STYLE_BY_RUFF
from tests.test_style import LIST_COMMAND_EXPECTED_STYLE_NO_RUFF
from tests.test_style import LIST_COMMAND_EXPECTED_STYLE_WITHOUT_RUFF_BY_RUFF
from tests.testlibraries import check_list_result

if TYPE_CHECKING:
    from invoke import Context

PYTHON_DIR_EXCLUDING_TEST = "invokelint setup.py tasks.py"
TEST_DIR = "tests"
PYTHON_DIR = f"{PYTHON_DIR_EXCLUDING_TEST} {TEST_DIR}"
COMMAND_EXPECTED_RADON_CC = f"radon cc {PYTHON_DIR}"
COMMAND_EXPECTED_RADON_MI = f"radon mi {PYTHON_DIR}"
COMMAND_EXPECTED_RUFF_CHECK = f"ruff check {PYTHON_DIR}"
COMMAND_EXPECTED_BANDIT = f"bandit --configfile pyproject.toml --recursive {PYTHON_DIR}"
COMMAND_EXPECTED_DODGY = "dodgy --ignore-paths csvinput"
COMMAND_EXPECTED_FLAKE8 = f"flake8 --radon-show-closures {PYTHON_DIR}"
COMMAND_EXPECTED_PYDOCSTYLE = f"pydocstyle {PYTHON_DIR}"
COMMAND_EXPECTED_XENON = f"xenon --max-absolute A --max-modules A --max-average A {PYTHON_DIR}"
COMMAND_EXPECTED_MYPY = f"mypy {PYTHON_DIR}"
COMMAND_EXPECTED_PYLINT = f"pylint {PYTHON_DIR}"
COMMAND_EXPECTED_SEMGREP = (
    f"semgrep scan --oss-only --config auto {' '.join([f'--include {code}' for code in PYTHON_DIR.split(' ')])}"
)


def test_radon_cc(context: "Context") -> None:
    check_list_result(radon_cc(context), [COMMAND_EXPECTED_RADON_CC])


def test_radon_mi(context: "Context") -> None:
    check_list_result(radon_mi(context), [COMMAND_EXPECTED_RADON_MI])


def test_radon(context: "Context") -> None:
    list_command_expected = [COMMAND_EXPECTED_RADON_CC, COMMAND_EXPECTED_RADON_MI]
    list_result = radon(context)
    check_list_result(list_result, list_command_expected)


def test_cohesion(context: "Context") -> None:
    """Function: cohesion() should run appropriate commands."""
    list_command_expected = [
        "cohesion --directory invokelint",
        "cohesion --directory setup.py",
        "cohesion --directory tasks.py",
        "cohesion --directory tests",
    ]
    list_result = cohesion(context)
    check_list_result(list_result, list_command_expected)


def test_ruff(context: "Context") -> None:
    check_list_result(ruff_task(context), [COMMAND_EXPECTED_RUFF_CHECK])


def test_bandit(context: "Context") -> None:
    check_list_result(bandit(context), [COMMAND_EXPECTED_BANDIT])


def test_dodgy(context: "Context") -> None:
    check_list_result(dodgy(context), [COMMAND_EXPECTED_DODGY])


def test_flake8(context: "Context") -> None:
    check_list_result(flake8(context), [COMMAND_EXPECTED_FLAKE8])


def test_pydocstyle(context: "Context") -> None:
    check_list_result(pydocstyle(context), [COMMAND_EXPECTED_PYDOCSTYLE])


def test_xenon(context: "Context") -> None:
    check_list_result(xenon(context), [COMMAND_EXPECTED_XENON])


LIST_COMMAND_EXPECTED = [
    COMMAND_EXPECTED_XENON,
    COMMAND_EXPECTED_RUFF_CHECK,
    COMMAND_EXPECTED_BANDIT,
    COMMAND_EXPECTED_DODGY,
    COMMAND_EXPECTED_FLAKE8,
]


def test_fast(context: "Context") -> None:
    """Command should success and run appropriate commands."""
    list_result = fast(context)
    check_list_result(list_result, LIST_COMMAND_EXPECTED_STYLE_BY_RUFF + LIST_COMMAND_EXPECTED)


def test_fast_pydocstyle(context: "Context") -> None:
    """Command should success and run appropriate commands."""
    list_result = fast(context, pydocstyle=True)
    check_list_result(
        list_result,
        LIST_COMMAND_EXPECTED_STYLE_BY_RUFF + LIST_COMMAND_EXPECTED + [COMMAND_EXPECTED_PYDOCSTYLE],
    )


def test_fast_ruff(context: "Context") -> None:
    """Command should success and run appropriate commands."""
    list_result = fast(context, ruff=True)
    check_list_result(list_result, LIST_COMMAND_EXPECTED_STYLE_WITHOUT_RUFF_BY_RUFF + LIST_COMMAND_EXPECTED)


def test_fast_skip_format(context: "Context") -> None:
    """Command should success and run appropriate commands."""
    list_result = fast(context, skip_format=True)
    check_list_result(list_result, LIST_COMMAND_EXPECTED)


def test_fast_by_ruff(context: "Context") -> None:
    """Command should success and run appropriate commands."""
    list_result = fast(context, by_ruff=True)
    check_list_result(list_result, LIST_COMMAND_EXPECTED_STYLE_BY_RUFF + LIST_COMMAND_EXPECTED)


def test_fast_no_ruff(context: "Context") -> None:
    """Command should success and run appropriate commands."""
    list_result = fast(context, no_ruff=True)
    check_list_result(list_result, LIST_COMMAND_EXPECTED_STYLE_NO_RUFF + LIST_COMMAND_EXPECTED)


@pytest.mark.slow
def test_mypy(context: "Context") -> None:
    check_list_result(mypy(context), [COMMAND_EXPECTED_MYPY])


@pytest.mark.slow
def test_pylint(context: "Context") -> None:
    check_list_result(pylint(context), [COMMAND_EXPECTED_PYLINT])


@pytest.mark.slow
# - semgrep does not work on windows 10 · Issue #4295 · returntocorp/semgrep
#   https://github.com/returntocorp/semgrep/issues/4295
# - No module found: resource (ModuleNotFoundError) · Issue #7146 · returntocorp/semgrep
#   https://github.com/returntocorp/semgrep/issues/7146
@pytest.mark.skipif(sys.platform == "win32", reason="Semgrep doesn't support Windows.")
def test_semgrep(context: "Context") -> None:
    """Command should success and run appropriate commands."""
    check_list_result(semgrep(context), [COMMAND_EXPECTED_SEMGREP])


@pytest.mark.slow
def test_deep(context: "Context") -> None:
    """Command should success and run appropriate commands."""
    list_command_expected = [COMMAND_EXPECTED_MYPY, COMMAND_EXPECTED_PYLINT]
    if platform.system() != "Windows":
        list_command_expected.append(COMMAND_EXPECTED_SEMGREP)
    list_result = deep(context)
    check_list_result(list_result, list_command_expected)
