"""Tests for `test` package."""

import platform
import re
from textwrap import dedent
from typing import TYPE_CHECKING

from invoke import MockContext
from invoke import Result

from invokelint.test import build_coverage_run_command
from invokelint.test import coverage
from invokelint.test import fast
from invokelint.test import run_test_all
from tests.testlibraries import check_list_result
from tests.testlibraries import check_result

if TYPE_CHECKING:
    from pytest_mock import MockFixture

EXPECTED_STDOUT = dedent(
    """\
        ================== test session starts ====================
        platform linux -- Python 3.11.1, pytest-7.2.1, pluggy-1.0.0
        rootdir: /workspace
        collected 17 items

        tests/test_lint.py ............                      [ 70%]
        tests/test_run.py .                                  [ 76%]
        tests/test_style.py ..                               [ 88%]
        tests/test_test.py ....                              [100%]
        ================== 17 passed in 12.61s ====================
    """,
)


def test_fast() -> None:
    """The test task should call pytest."""
    # Windows cmd.exe requires to so surround "not slow" by double quote,
    # otherwise, following error raised:
    #   ERROR: file or directory not found: slow'
    # - Answer: cmd - What does single-quoting do in Windows batch files? - Stack Overflow
    #   https://stackoverflow.com/a/24181667/12721873
    expected_command = 'pytest -m "not slow" -vv'
    expected_pty = platform.system() == "Linux"
    context = MockContext(run={expected_command: Result(EXPECTED_STDOUT)})
    check_result(fast(context), expected_command)
    # Reason: The invoke-typed not implemented. pylint: disable=no-member
    context.run.assert_called_with(expected_command, pty=expected_pty)  # type: ignore[attr-defined]


def test_run_test_all() -> None:
    """The test task should call pytest."""
    expected_command = "pytest -vv"
    expected_pty = platform.system() == "Linux"
    context = MockContext(run={expected_command: Result(EXPECTED_STDOUT)})
    check_result(run_test_all(context), expected_command)
    # Reason: The invoke-typed not implemented. pylint: disable=no-member
    context.run.assert_called_with(expected_command, pty=expected_pty)  # type: ignore[attr-defined]


EXPECTED_STDOUT_REPORT = dedent(
    """\
        Name                     Stmts   Miss  Cover   Missing
        ------------------------------------------------------
        invokelint/__init__.py       3      0   100%
        invokelint/lint.py          56      0   100%
        invokelint/path.py          11      0   100%
        invokelint/run.py           18      0   100%
        invokelint/style.py         33      0   100%
        invokelint/test.py          28      0   100%
        ------------------------------------------------------
        TOTAL                      149     11   100%
    """,
)
EXPECTED_COMMAND_RUN = "coverage run --source invokelint -m pytest"
EXPECTED_COMMAND_REPORT = "coverage report --show-missing"


def test_build_coverage_run_command() -> None:
    assert build_coverage_run_command(is_all=True) == "coverage run --source invokelint,setup,tasks -m pytest"


def test_coverage(mocker: "MockFixture") -> None:
    """The test task should call coverage."""
    context = MockContext(
        run={
            EXPECTED_COMMAND_RUN: Result(EXPECTED_STDOUT),
            EXPECTED_COMMAND_REPORT: Result(EXPECTED_STDOUT_REPORT),
        },
    )
    expected_pty = platform.system() == "Linux"
    check_list_result(coverage(context), [EXPECTED_COMMAND_REPORT])
    calls = [
        mocker.call(EXPECTED_COMMAND_RUN, pty=expected_pty),
        mocker.call(EXPECTED_COMMAND_REPORT, pty=expected_pty),
    ]
    # Reason: The invoke-typed not implemented. pylint: disable=no-member
    context.run.assert_has_calls(calls)  # type: ignore[attr-defined]


def test_coverage_publish(mocker: "MockFixture") -> None:
    """The test task should call coveralls."""
    expected_command_publish = "coveralls"
    context = MockContext(
        run={
            EXPECTED_COMMAND_RUN: Result(EXPECTED_STDOUT),
            EXPECTED_COMMAND_REPORT: Result(EXPECTED_STDOUT_REPORT),
            expected_command_publish: Result(EXPECTED_STDOUT_REPORT),
        },
    )
    expected_pty = platform.system() == "Linux"
    check_list_result(coverage(context, publish=True), [EXPECTED_COMMAND_REPORT, expected_command_publish])
    calls = [
        mocker.call(EXPECTED_COMMAND_RUN, pty=expected_pty),
        mocker.call(EXPECTED_COMMAND_REPORT, pty=expected_pty),
        mocker.call(expected_command_publish, pty=expected_pty),
    ]
    # Reason: The invoke-typed not implemented. pylint: disable=no-member
    context.run.assert_has_calls(calls)  # type: ignore[attr-defined]


def test_coverage_xml_html(mocker: "MockFixture") -> None:
    """The test task should call coverage xml, coverage html."""
    expected_command_xml = "coverage xml"
    expected_command_html = "coverage html"
    expected_pty = platform.system() == "Linux"
    mock_open = mocker.MagicMock()
    mocker.patch("webbrowser.open", mock_open)
    context = MockContext(
        run={
            EXPECTED_COMMAND_RUN: Result(EXPECTED_STDOUT),
            EXPECTED_COMMAND_REPORT: Result(EXPECTED_STDOUT_REPORT),
            expected_command_xml: Result(EXPECTED_STDOUT_REPORT),
            expected_command_html: Result(EXPECTED_STDOUT_REPORT),
        },
    )
    check_list_result(
        coverage(context, xml=True, html=True),
        [EXPECTED_COMMAND_REPORT, expected_command_xml, expected_command_html],
    )
    calls = [
        mocker.call(EXPECTED_COMMAND_RUN, pty=expected_pty),
        mocker.call(EXPECTED_COMMAND_REPORT, pty=expected_pty),
        mocker.call(expected_command_xml, pty=expected_pty),
        mocker.call(expected_command_html, pty=expected_pty),
    ]
    # Reason: The invoke-typed not implemented. pylint: disable=no-member
    context.run.assert_has_calls(calls)  # type: ignore[attr-defined]
    args = mock_open.call_args[0]
    assert len(args) == 1
    assert re.fullmatch(r"file:\/\/.*index\.html", args[0])
