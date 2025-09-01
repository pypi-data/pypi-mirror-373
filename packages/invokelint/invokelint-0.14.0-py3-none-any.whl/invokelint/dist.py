"""Tasks of build."""

import builtins

from invoke import Collection
from invoke import Context
from invoke import Result
from invoke import task

from invokelint._clean import clean_all
from invokelint.run import run_in_pty

ns = Collection()


def module_exists(module_name: str) -> bool:
    """To minimize try block."""
    try:
        # Reason:
        #   F401: Just check existence, use it via command line.
        #   RUF100: Ruff 0.0.254 started to report that unused: `F401`,
        #           however Flake8 running in Python still requires `F401`.
        builtins.__import__(module_name)  # noqa: F401,RUF100 pylint: disable=import-outside-toplevel,unused-import
    except ModuleNotFoundError:
        return False
    return True


@task(clean_all)
def dist(context: Context) -> Result:
    """Builds source and wheel packages into dist/ directory."""
    if module_exists("build"):
        return run_in_pty(context, "python -m build")
    if module_exists("wheel"):
        run_in_pty(context, "python setup.py sdist")
        return run_in_pty(context, "python setup.py bdist_wheel")
    msg = "Neither build nor wheel module exists. Run `pip install build` or `pip install wheel`."
    raise ModuleNotFoundError(msg)


ns.add_task(dist, default=True)
