from __future__ import annotations

import click


def emptyable_opt_list_callback(
    ctx: click.Context, param: click.Parameter, value: tuple[str, ...]
) -> list[str] | None:
    """
    A callback which converts multiple=True options as follows:
    - empty results, () => None
    - ("",) => []
    - * => passthrough
    """
    if len(value) == 0:
        return None
    if value == ("",):
        return []
    return list(value)
