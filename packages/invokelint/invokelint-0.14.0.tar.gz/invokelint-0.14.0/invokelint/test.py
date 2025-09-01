"""Tasks of test."""

from __future__ import annotations

import webbrowser
from pathlib import Path

from invoke import Collection
from invoke import Context
from invoke import Result
from invoke import task

from invokelint.path import PRODUCTION_PACKAGES
from invokelint.path import PYTHON_DIRS_EXCLUDING_TEST
from invokelint.run import run_in_pty

ns = Collection()


@task
def fast(context: Context) -> Result:
    """Runs fast tests (not mark @pytest.mark.slow)."""
    # Windows cmd.exe requires to so surround "not slow" by double quote,
    # otherwise, following error raised:
    #   ERROR: file or directory not found: slow'
    # - Answer: cmd - What does single-quoting do in Windows batch files? - Stack Overflow
    #   https://stackoverflow.com/a/24181667/12721873
    return run_in_pty(context, 'pytest -m "not slow" -vv')


ns.add_task(fast, default=True)


@task(name="all")
def run_test_all(context: Context) -> Result:
    """Runs all tests."""
    return run_in_pty(context, "pytest -vv")


ns.add_task(run_test_all)


def build_coverage_run_command(*, is_all: bool = False) -> str:
    """To seel complexity of building Coverage.py run command."""
    targets = PYTHON_DIRS_EXCLUDING_TEST if is_all else PRODUCTION_PACKAGES
    # Coverage.py Currently can't apply any options including --source when multiprocessing:
    #   Options affecting multiprocessing must only be specified in a configuration file.
    #   Remove --source from the command line.
    #   Use 'coverage help' for help.
    #   Full documentation is at https://coverage.readthedocs.io
    # Reason: Note. pylint: disable=line-too-long
    # command = "coverage run --concurrency=multiprocessing --source {} -m pytest".format(",".join(targets))  # noqa: ERA001
    return f"coverage run --source {','.join(Path(target).stem for target in targets)} -m pytest"


@task(
    help={
        "all": "Target all python files excluding tests.",
        "publish": "Publish the result via coveralls",
        "xml": "Export report as xml format",
        "html": "Export report as html format and open it in browser",
    },
    aliases=("cov",),
)
def coverage(
    context: Context,
    *,
    # Reason: To name command line option.
    all: bool = False,  # noqa: A002  pylint: disable=redefined-builtin
    publish: bool = False,
    xml: bool = False,
    html: bool = False,
) -> list[Result]:
    """Runs all tests and report coverage (options for create xml / html available)."""
    run_in_pty(context, build_coverage_run_command(is_all=all))
    result = []
    # Reason: Note.
    # result = run_in_pty(context, "coverage combine")  # noqa: ERA001
    result.append(run_in_pty(context, "coverage report --show-missing"))
    if publish:
        # Publish the results via coveralls
        result.append(run_in_pty(context, "coveralls"))
        return result
    # Build a local report
    if xml:
        result.append(run_in_pty(context, "coverage xml"))
    if html:
        result.append(run_in_pty(context, "coverage html"))
        # as_url() with relative path raises following error:
        #   ValueError: relative path can't be expressed as a file URI
        # Path.absolute() for Python 3.9 or less in Windows.
        # see:
        # - Pathlib absolute() vs. resolve() - Python Help - Discussions on Python.org
        #   https://discuss.python.org/t/pathlib-absolute-vs-resolve/2573/18
        webbrowser.open(Path("index.html").absolute().resolve().as_uri())
    return result


ns.add_task(coverage)
