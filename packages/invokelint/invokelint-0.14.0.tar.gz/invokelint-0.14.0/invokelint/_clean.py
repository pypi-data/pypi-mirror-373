"""Tasks of clean."""

from __future__ import annotations

import shutil
import sys
from contextlib import suppress
from pathlib import Path

from invoke import Collection
from invoke import Context
from invoke import Result
from invoke import task

from invokelint.run import run_all
from invokelint.run import run_in_pty

ROOT_DIR = Path(__file__).parent
COVERAGE_FILE = ROOT_DIR.joinpath(".coverage")
COVERAGE_DIR = ROOT_DIR.joinpath("htmlcov")

ns = Collection()


@task
def dist(context: Context) -> list[Result]:
    """Cleans up files from package building."""
    return [
        run_in_pty(context, "rm -fr build/"),
        run_in_pty(context, "rm -fr dist/"),
        run_in_pty(context, "rm -fr .eggs/"),
        run_in_pty(context, "find . -name '*.egg-info' -exec rm -fr {} +"),
        run_in_pty(context, "find . -name '*.egg' -not -path '*/.venv/*' -exec rm -f {} +"),
    ]


ns.add_task(dist)


@task
def python(context: Context) -> list[Result]:
    """Cleans up python file artifacts."""
    return [
        run_in_pty(context, "find . -name '*.pyc' -exec rm -f {} +"),
        run_in_pty(context, "find . -name '*.pyo' -exec rm -f {} +"),
        run_in_pty(context, "find . -name '*~' -exec rm -f {} +"),
        run_in_pty(context, "find . -name '__pycache__' -exec rm -fr {} +"),
    ]


ns.add_task(python)


def _delete_file(file: Path) -> None:
    if sys.version_info >= (3, 8):
        return file.unlink(missing_ok=True)
    return _delete_file_legacy(file)  # pragma: no cover


def _delete_file_legacy(file: Path) -> None:  # pragma: no cover
    # Reason: The command doesn't expects file exists.
    with suppress(FileNotFoundError):
        file.unlink()


@task
def tests(_context: Context) -> list[Result]:
    """Cleans up files from testing."""
    _delete_file(COVERAGE_FILE)
    shutil.rmtree(COVERAGE_DIR, ignore_errors=True)
    return [Result()]


ns.add_task(tests)


@task(name="all")
def clean_all(context: Context) -> list[Result]:
    """Cleans up all."""
    return run_all([dist, python, tests], context)


ns.add_task(clean_all, default=True)
