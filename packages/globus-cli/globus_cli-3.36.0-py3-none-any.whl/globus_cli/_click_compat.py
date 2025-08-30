"""
A compatibility module for handling click v8.2.0+ and 8.1.x API differences.
"""

import functools
import importlib.metadata
import typing as t

import click

C = t.TypeVar("C", bound=t.Callable[..., t.Any])

CLICK_VERSION = importlib.metadata.version("click")

OLDER_CLICK_API = CLICK_VERSION.startswith("8.1.")
NEWER_CLICK_API = not OLDER_CLICK_API


def shim_get_metavar(f: C) -> C:
    """
    Make a ParamType.get_metavar function compatible with both the 8.1.x and
    the 8.2.0+ APIs.

    Under 8.2.0, `ctx: click.Context` is passed, while older versions do not.
    Therefore, do nothing on 8.2.0+ and pass `ctx=None' if the older click
    version is in use.

    NOTE: we pass `ctx=None` which violates the declared types (but works at
    runtime) because when running under older click versions, there may not be
    a current click context.
    """
    if OLDER_CLICK_API:

        @functools.wraps(f)
        def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
            return f(*args, **kwargs, ctx=None)

        return wrapper  # type: ignore[return-value]

    return f


def shim_get_missing_message(f: C) -> C:
    """
    Shim `get_missing_message` in a similar way to `get_metavar` above.
    """
    if OLDER_CLICK_API:

        @functools.wraps(f)
        def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
            return f(*args, **kwargs, ctx=click.get_current_context())

        return wrapper  # type: ignore[return-value]

    return f
