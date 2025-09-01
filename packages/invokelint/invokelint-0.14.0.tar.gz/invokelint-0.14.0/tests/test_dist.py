"""Tests for `dist` package."""

from typing import TYPE_CHECKING

import pytest

from invokelint.dist import dist
from invokelint.dist import module_exists
from tests.testlibraries import check_result

if TYPE_CHECKING:
    from invoke import Context


@pytest.mark.usefixtures("_package_not_exists")
@pytest.mark.parametrize(
    ("package_names", "parameter", "expect"),
    [
        ([], "build", True),
        (["build"], "build", False),
    ],
)
def test_module_exists(parameter: str, *, expect: bool) -> None:
    """Function: module_exists() should return False if fail to import build module."""
    assert module_exists(parameter) == expect


@pytest.mark.slow
def test_dist_build(context: "Context") -> None:
    check_result(dist(context), "python -m build")


@pytest.mark.slow
@pytest.mark.usefixtures("_package_not_exists")
@pytest.mark.parametrize("package_names", [["build"]])
def test_dist_setup_py(context: "Context") -> None:
    check_result(dist(context), "python setup.py bdist_wheel")


@pytest.mark.usefixtures("_package_not_exists")
@pytest.mark.parametrize("package_names", [["build", "wheel"]])
def test_dist_error(context: "Context") -> None:
    with pytest.raises(ModuleNotFoundError, match="Neither build nor wheel module exists."):
        check_result(dist(context), "python setup.py bdist_wheel")
