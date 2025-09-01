"""Tests for `run` package."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest
from invoke import Context
from invoke import Result
from invoke import UnexpectedExit
from invoke import task

from invokelint.run import run_all

if TYPE_CHECKING:
    from pathlib import Path


@task
def fail(context: Context) -> list[Result]:
    if sys.platform == "win32":
        return [context.run("exit /b 1", pty=False)]
    return [context.run("exit 1")]


@task
def create_file(context: Context) -> list[Result]:
    """Stub for testing run_all()."""
    file_name = "test.txt"
    if sys.platform == "win32":
        return [
            context.run(f"copy /b NUL {file_name}", pty=False),
            context.run("dir", pty=False),
        ]
    return [context.run(f"touch {file_name}")]


@pytest.mark.skipif(sys.platform == "win32", reason="Code: context.cd() works only in Linux.")
def test_create_file_linux(tmp_path: Path, context: Context) -> None:
    """see:

    - Changing directories between drives on Windows doesn't work · Issue #755 · pyinvoke/invoke
      https://github.com/pyinvoke/invoke/issues/755
    """
    with context.cd(str(tmp_path.resolve())):
        check_created_file(tmp_path, context, 1)


@pytest.mark.skipif(sys.platform != "win32", reason="Code: cd /d works only in Windows.")
def test_create_file_windows(tmp_path: Path, context: Context) -> None:
    """see:

    - Changing directories between drives on Windows doesn't work · Issue #755 · pyinvoke/invoke
      https://github.com/pyinvoke/invoke/issues/755
    """
    with context.prefix(f"cd /d {tmp_path.resolve()!s}"):
        check_created_file(tmp_path, context, 2)


def check_created_file(tmp_path: Path, context: Context, expected_length: int) -> None:
    list_result = create_file(context)
    assert len(list_result) == expected_length
    for result in list_result:
        assert result.return_code == 0
    assert (tmp_path / "test.txt").exists()


@pytest.mark.skipif(sys.platform == "win32", reason="Code: context.cd() works only in Linux.")
def test_run_all_linux(tmp_path: Path, context: Context) -> None:
    """All commands should be run even one of them failed.

    see:
    - Changing directories between drives on Windows doesn't work · Issue #755 · pyinvoke/invoke
      https://github.com/pyinvoke/invoke/issues/755
    """
    list_expected_message = ["Encountered a bad command exit code!", "Exit code: 1"]
    with context.cd(str(tmp_path.resolve())), pytest.raises(UnexpectedExit) as excinfo:
        run_all([fail, create_file], context)
    check_run_all(list_expected_message, excinfo.value, tmp_path)


@pytest.mark.skipif(sys.platform != "win32", reason="Code: cd /d works only in Windows.")
def test_run_all_windows(tmp_path: Path, context: Context) -> None:
    """All commands should be run even one of them failed.

    see:
    - Changing directories between drives on Windows doesn't work · Issue #755 · pyinvoke/invoke
      https://github.com/pyinvoke/invoke/issues/755
    """
    list_expected_message = ["Encountered a bad command exit code!", "Exit code: 1"]
    with context.prefix(f"cd /d {tmp_path.resolve()!s}"), pytest.raises(UnexpectedExit) as excinfo:
        run_all([fail, create_file], context)
    check_run_all(list_expected_message, excinfo.value, tmp_path)


def check_run_all(list_expected_message: list[str], error: UnexpectedExit, tmp_path: Path) -> None:
    for expected_message in list_expected_message:
        assert expected_message in str(error)
    assert (tmp_path / "test.txt").exists()
