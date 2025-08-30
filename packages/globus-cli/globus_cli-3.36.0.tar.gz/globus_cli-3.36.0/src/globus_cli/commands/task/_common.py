from __future__ import annotations

import typing as t

import click

from globus_cli.types import AnyCommand

C = t.TypeVar("C", bound=AnyCommand)


def task_id_arg(*, required: bool = True) -> t.Callable[[C], C]:
    """
    By default, the task ID is made required; pass `required=False` to the
    decorator arguments to make it optional.
    """
    return click.argument("TASK_ID", type=click.UUID, required=required)
