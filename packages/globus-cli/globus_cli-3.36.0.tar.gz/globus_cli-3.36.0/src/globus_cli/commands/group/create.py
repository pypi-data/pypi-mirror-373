from __future__ import annotations

import uuid

import click

from globus_cli.login_manager import LoginManager
from globus_cli.parsing import command
from globus_cli.termio import display


@command("create")
@click.argument("name")
@click.option("--description", help="Description for the group")
@click.option(
    "--parent-id",
    type=click.UUID,
    help=(
        "Make the new group a subgroup of the specified parent group. "
        "You must be an admin of the parent group to do this."
    ),
)
@LoginManager.requires_login("groups")
def group_create(
    login_manager: LoginManager,
    *,
    name: str,
    description: str | None,
    parent_id: uuid.UUID | None,
) -> None:
    """Create a new group."""
    groups_client = login_manager.get_groups_client()

    response = groups_client.create_group(
        {
            "name": name,
            "description": description,
            "parent_id": parent_id,
        }
    )
    group_id = response["id"]

    display(response, simple_text=f"Group {group_id} created successfully")
