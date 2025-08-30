import typing as t

import click

from globus_cli.termio import formatters
from globus_cli.types import AnyCommand

C = t.TypeVar("C", bound=AnyCommand)


class RolePrincipalFormatter(formatters.auth.PrincipalDictFormatter):
    def render_group_id(self, group_id: str) -> str:
        return f"https://app.globus.org/groups/{group_id}"


def role_id_arg(f: C) -> C:
    return click.argument("role_id")(f)
