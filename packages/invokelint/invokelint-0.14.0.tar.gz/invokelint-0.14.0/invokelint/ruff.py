"""To unify executing Ruff from style and from lint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from invokelint.path import PYTHON_DIRS
from invokelint.run import run_in_pty

if TYPE_CHECKING:
    from invoke import Context
    from invoke import Result


def chk(context: Context, *, fix: bool = False, show_fixes: bool = False, warn: bool = False) -> list[Result]:
    """Lints code with Ruff."""
    list_options = []
    if fix:
        list_options.append("--fix")
    if show_fixes:
        list_options.append("--show-fixes")
    options = " " + " ".join(list_options) if list_options else ""
    return [run_in_pty(context, f"ruff check{options} {' '.join(PYTHON_DIRS)}", warn=warn)]


def fmt(context: Context, *, diff: bool = False, warn: bool = False) -> list[Result]:
    """Lints code with Ruff."""
    list_options = []
    if diff:
        list_options.append("--diff")
    options = " " + " ".join(list_options) if list_options else ""
    return [run_in_pty(context, f"ruff format{options} {' '.join(PYTHON_DIRS)}", warn=warn)]
