"""Tasks of format."""

from __future__ import annotations

from typing import Any

from invoke import Collection
from invoke import Context
from invoke import Result
from invoke import task
from invoke.exceptions import Exit

from invokelint import ruff as ruff_commands
from invokelint.path import PYTHON_DIRS
from invokelint.run import run_in_order
from invokelint.run import run_in_pty

ns = Collection()


# Reason: Compatibility with semgrep task to be called from lint.fast().. pylint: disable=unused-argument
def docformatter(context: Context, *, check: bool = False, **kwargs: Any) -> list[Result]:  # noqa: ARG001
    """Runs docformatter.

    This function includes hard coding of line length.
    see:
    - Add pyproject.toml support for config (Issue #10) by weibullguy · Pull Request #77 · PyCQA/docformatter
    https://github.com/PyCQA/docformatter/pull/77
    """
    docformatter_options = f" --recursive {'--check' if check else '--in-place'}"
    return [run_in_pty(context, f"docformatter{docformatter_options} {' '.join(PYTHON_DIRS)}", warn=True)]


# Reason: Compatibility with semgrep task to be called from lint.fast().. pylint: disable=unused-argument
def autoflake(context: Context, *, check: bool = False, **kwargs: Any) -> list[Result]:  # noqa: ARG001
    """Runs autoflake."""
    autoflake_options = f" --recursive {'--check' if check else '--in-place'}"
    return [run_in_pty(context, f"autoflake{autoflake_options} {' '.join(PYTHON_DIRS)}", warn=True)]


# Reason: Compatibility with semgrep task to be called from lint.fast().. pylint: disable=unused-argument
def isort(context: Context, *, check: bool = False, **kwargs: Any) -> list[Result]:  # noqa: ARG001
    """Runs isort."""
    isort_options = " --check-only --diff" if check else ""
    return [run_in_pty(context, f"isort{isort_options} {' '.join(PYTHON_DIRS)}", warn=True)]


# Reason: Compatibility with semgrep task to be called from lint.fast().. pylint: disable=unused-argument
def black(context: Context, *, check: bool = False, **kwargs: Any) -> list[Result]:  # noqa: ARG001
    """Runs Black."""
    black_options = " --check --diff" if check else ""
    return [run_in_pty(context, f"black{black_options} {' '.join(PYTHON_DIRS)}", warn=True)]


# Reason: Compatibility with semgrep task to be called from lint.fast().. pylint: disable=unused-argument
def call_ruff_check(context: Context, *, check: bool = False, **kwargs: Any) -> list[Result]:  # noqa: ARG001
    if check:
        return ruff_commands.chk(context, show_fixes=True)
    result = []
    result.extend(ruff_commands.chk(context, show_fixes=True, warn=True))
    result.extend(ruff_commands.chk(context, fix=True, show_fixes=True))
    return result


# Reason: Compatibility with semgrep task to be called from lint.fast().. pylint: disable=unused-argument
def call_ruff_fmt(context: Context, *, check: bool = False, **kwargs: Any) -> list[Result]:  # noqa: ARG001
    if check:
        return ruff_commands.fmt(context, diff=check)
    result = []
    result.extend(ruff_commands.fmt(context, diff=True, warn=True))
    result.extend(ruff_commands.fmt(context))
    return result


def is_ruff(*, by_ruff: bool, no_ruff: bool) -> bool:
    """Determines if Ruff should be used for formatting."""
    if by_ruff and no_ruff:
        msg = "Cannot use both '--by-ruff' and '--no-ruff' options together."
        raise Exit(msg)
    return by_ruff or not no_ruff


@task(
    help={
        "check": "Checks if source is formatted without applying changes",
        "ruff": "Leaves Ruff warnings not fixed (not apply `ruff check --fix`, only `ruff format` is applied)",
        "by_ruff": "Formats code by Ruff (default)",
        "no_ruff": "Formats code by autoflake, isort, and Black (requires to install them)",
    },
)
def fmt(
    context: Context,
    *,
    check: bool = False,
    ruff: bool = False,
    by_ruff: bool = False,
    no_ruff: bool = False,
) -> list[Result]:
    """Formats code by docformatter and Ruff (option for only check available)."""
    tasks = [docformatter]
    tasks.extend([call_ruff_fmt] if is_ruff(by_ruff=by_ruff, no_ruff=no_ruff) else [autoflake, isort, black])
    if check or not ruff:
        tasks.append(call_ruff_check)
    return run_in_order(tasks, context, check=check)


ns.add_task(fmt, default=True)
