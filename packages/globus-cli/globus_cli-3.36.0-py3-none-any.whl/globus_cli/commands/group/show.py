import uuid

from globus_cli.login_manager import LoginManager
from globus_cli.parsing import command
from globus_cli.termio import display

from ._common import GROUP_FIELDS, GROUP_FIELDS_W_SUBSCRIPTION, group_id_arg


@group_id_arg
@command("show")
@LoginManager.requires_login("groups")
def group_show(login_manager: LoginManager, *, group_id: uuid.UUID) -> None:
    """Show a group definition."""
    groups_client = login_manager.get_groups_client()

    group = groups_client.get_group(group_id, include="my_memberships")

    if group.get("subscription_id") is not None:
        fields = GROUP_FIELDS_W_SUBSCRIPTION
    else:
        fields = GROUP_FIELDS

    display(group, text_mode=display.RECORD, fields=fields)
