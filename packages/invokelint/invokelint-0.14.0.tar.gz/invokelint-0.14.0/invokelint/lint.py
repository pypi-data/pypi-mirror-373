"""Tasks of lint."""

from __future__ import annotations

import platform
from typing import TYPE_CHECKING
from typing import Any

from invoke import Collection
from invoke import Context
from invoke import Result
from invoke import task

from invokelint import ruff as ruff_commands
from invokelint.path import PYTHON_DIRS
from invokelint.run import run_all
from invokelint.run import run_in_order
from invokelint.run import run_in_pty
from invokelint.style import fmt

if TYPE_CHECKING:
    from invokelint.run import TaskFunction

ns = Collection()


@task
def radon_cc(context: Context) -> list[Result]:
    """Reports code complexity."""
    return [context.run(f"radon cc {' '.join(PYTHON_DIRS)}")]


@task
def radon_mi(context: Context) -> list[Result]:
    """Reports maintainability index."""
    return [context.run(f"radon mi {' '.join(PYTHON_DIRS)}")]


@task
def radon(context: Context) -> list[Result]:
    """Reports radon both code complexity and maintainability index."""
    return run_all([radon_cc, radon_mi], context)


ns.add_task(radon_cc)
ns.add_task(radon_mi)
ns.add_task(radon)


@task
def cohesion(context: Context) -> list[Result]:
    """Lints code with Cohesion."""
    # 2021-10-24:
    # Cohesion doesn't support multiple directories in 1 command.
    # Only the last directory enables when supply multiple --directory options.
    return [run_in_pty(context, f"cohesion --directory {directory}") for directory in PYTHON_DIRS]


ns.add_task(cohesion)


@task
def xenon(context: Context) -> list[Result]:
    """Checks code complexity."""
    command = f"xenon --max-absolute A --max-modules A --max-average A {' '.join(PYTHON_DIRS)}"
    return [run_in_pty(context, command)]


# Reason: Compatibility with semgrep task to be called from fast().. pylint: disable=unused-argument
def call_xenon(context: Context, **kwargs: Any) -> list[Result]:  # noqa: ARG001
    return xenon(context)


@task(name="ruff")
def ruff_task(context: Context) -> list[Result]:
    """Lints code with Ruff."""
    return ruff_commands.chk(context)


# Reason: Compatibility with semgrep task to be called from fast().. pylint: disable=unused-argument
def call_ruff(context: Context, **kwargs: Any) -> list[Result]:  # noqa: ARG001
    return ruff_task(context)


@task
def bandit(context: Context) -> list[Result]:
    """Lints code with bandit."""
    return [run_in_pty(context, f"bandit --configfile pyproject.toml --recursive {' '.join(PYTHON_DIRS)}")]


# Reason: Compatibility with semgrep task to be called from fast().. pylint: disable=unused-argument
def call_bandit(context: Context, **kwargs: Any) -> list[Result]:  # noqa: ARG001
    return bandit(context)


@task
def dodgy(context: Context) -> list[Result]:
    """Lints code with dodgy."""
    return [run_in_pty(context, "dodgy --ignore-paths csvinput")]


# Reason: Compatibility with semgrep task to be called from fast().. pylint: disable=unused-argument
def call_dodgy(context: Context, **kwargs: Any) -> list[Result]:  # noqa: ARG001
    return dodgy(context)


@task
def flake8(context: Context) -> list[Result]:
    """Lints code with flake8."""
    return [run_in_pty(context, f"flake8 --radon-show-closures {' '.join(PYTHON_DIRS)}")]


# Reason: Compatibility with semgrep task to be called from fast().. pylint: disable=unused-argument
def call_flake8(context: Context, **kwargs: Any) -> list[Result]:  # noqa: ARG001
    return flake8(context)


@task
def pydocstyle(context: Context) -> list[Result]:
    """Lints code with pydocstyle."""
    return [run_in_pty(context, f"pydocstyle {' '.join(PYTHON_DIRS)}")]


# Reason: Compatibility with semgrep task to be called from fast().. pylint: disable=unused-argument
def call_pydocstyle(context: Context, **kwargs: Any) -> list[Result]:  # noqa: ARG001
    return pydocstyle(context)


@task(
    help={
        "skip_format": "Lints without format style.",
        "ruff": "Leaves Ruff warnings not fixed (not apply `ruff check --fix`, only `ruff format` is applied)",
        "by_ruff": "Formats code by Ruff",
        "no_ruff": "Formats code by autoflake, isort, and Black (requires to install them)",
        "pydocstyle": "Runs pydocstyle",
    },
)
# Reason: For specification  pylint: disable=too-many-arguments
def fast(  # noqa: PLR0913
    context: Context,
    *,
    skip_format: bool = False,
    ruff: bool = False,
    by_ruff: bool = False,
    no_ruff: bool = False,
    # Reason: To name command line option.
    pydocstyle: bool = False,  # pylint: disable=redefined-outer-name
) -> list[Result]:
    """Runs fast linting (xenon, ruff, bandit, dodgy, flake8, pydocstyle).

    Xenon is prioritized since it effects fundamental coding structure.
    """
    list_result = [] if skip_format else fmt(context, ruff=ruff, by_ruff=by_ruff, no_ruff=no_ruff)
    tasks = [call_xenon, call_ruff, call_bandit, call_dodgy, call_flake8]
    if pydocstyle:
        tasks.append(call_pydocstyle)
    list_result.extend(run_in_order(tasks, context))
    return list_result


ns.add_task(xenon)
ns.add_task(ruff_task)
ns.add_task(bandit)
ns.add_task(dodgy)
ns.add_task(flake8)
ns.add_task(pydocstyle)
ns.add_task(fast, default=True)


@task
def mypy(context: Context) -> list[Result]:
    """Lints code with mypy."""
    return [run_in_pty(context, f"mypy {' '.join(PYTHON_DIRS)}")]


# Reason: Compatibility with semgrep task to be called from deep().. pylint: disable=unused-argument
def call_mypy(context: Context, **kwargs: Any) -> list[Result]:  # noqa: ARG001
    return mypy(context)


@task
def pylint(context: Context) -> list[Result]:
    """Lints code with Pylint."""
    return [run_in_pty(context, f"pylint {' '.join(PYTHON_DIRS)}")]


# Reason: Compatibility with semgrep task to be called from deep(). pylint: disable=unused-argument
def call_pylint(context: Context, **kwargs: Any) -> list[Result]:  # noqa: ARG001
    return pylint(context)


@task(help={"ci": "Run as CI mode."})
def semgrep(context: Context, *, ci: bool = False) -> list[Result]:
    """Lints code with Semgrep."""
    command = "ci" if ci else "scan"
    full_command = f"semgrep {command} --oss-only --config auto --include {' --include '.join(PYTHON_DIRS)}"
    return [run_in_pty(context, full_command)]


# Reason: Compatibility with semgrep task to be called from deep().. pylint: disable=unused-argument
def call_semgrep(context: Context, *, ci: bool = False, **kwargs: Any) -> list[Result]:  # noqa: ARG001
    return semgrep(context)


@task(help={"ci": "Run as CI mode."})
def deep(context: Context, *, ci: bool = False) -> list[Result]:
    """Runs slow but detailed linting (mypy, Pylint, semgrep)."""
    list_task: list[TaskFunction] = [call_mypy, call_pylint]
    if platform.system() != "Windows":
        list_task.append(call_semgrep)
    return run_in_order(list_task, context, ci=ci)


ns.add_task(mypy)
ns.add_task(pylint)
ns.add_task(semgrep)
ns.add_task(deep)
