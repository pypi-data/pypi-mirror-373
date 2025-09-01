"""Functions to run tasks."""

from __future__ import annotations

import platform
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import cast

from invoke import Context
from invoke import Result
from invoke import UnexpectedExit

if TYPE_CHECKING:
    from typing import Protocol

    class TaskFunction(Protocol):
        def __call__(self, context: Context, **kwargs: Any) -> list[Result]:  # pragma: no cover
            # fakeself gets swallowed by the class method binding logic
            # so this will match functions that have bar and the free arguments.
            ...


def run_in_pty(context: Context, command: str, **kwargs: Any) -> Result:
    return cast("Result", context.run(command, pty=platform.system() != "Windows", **kwargs))


def run_in_order(list_task: list[TaskFunction], context: Context, *args: Any, **kwargs: Any) -> list[Result]:
    """Runs tasks in order, stop subsequent tasks when task fail."""
    list_result = []
    for each_task in list_task:
        list_result.extend(each_task(context, *args, **kwargs))
    return list_result


def run_all(list_task: list[Callable[[Context], list[Result]]], context: Context) -> list[Result]:
    """Runs all commands even if failure."""
    list_unexpected_exit = []
    list_result = []
    for each_task in list_task:
        try:
            list_result.extend(each_task(context))
        # Reason: This loops only the time we can count
        except UnexpectedExit as error:  # noqa: PERF203
            list_unexpected_exit.append(error)
    if list_unexpected_exit:
        raise list_unexpected_exit[0]
    return list_result
