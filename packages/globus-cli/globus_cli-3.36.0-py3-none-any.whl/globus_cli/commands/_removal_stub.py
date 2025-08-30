from __future__ import annotations

import click

from globus_cli.parsing import command


@command(
    hidden=True,
    context_settings={"ignore_unknown_options": True},
    disable_options=(
        "format",
        "map_http_status",
    ),
)
@click.argument("UNKNOWN_ARG", nargs=-1)
def removal_stub_command(unknown_arg: tuple[str, ...]) -> None:
    """This command has been removed from the Globus CLI."""
    command_string = click.get_current_context().command_path
    click.echo(
        click.style(
            f"`{command_string}` has been removed from the Globus CLI.", fg="red"
        ),
        err=True,
    )
    click.get_current_context().exit(1)
