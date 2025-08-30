import uuid

import click

from globus_cli.login_manager import LoginManager
from globus_cli.parsing import command
from globus_cli.termio import display

from ._common import DELETED_TIMER_FORMAT_FIELDS


@command("delete", short_help="Delete a timer.")
@click.argument("TIMER_ID", type=click.UUID)
@LoginManager.requires_login("timers")
def delete_command(login_manager: LoginManager, *, timer_id: uuid.UUID) -> None:
    """
    Delete a timer.

    The contents of the deleted timer are printed afterward.
    """
    timer_client = login_manager.get_timer_client()
    deleted = timer_client.delete_job(timer_id)
    display(deleted, text_mode=display.RECORD, fields=DELETED_TIMER_FORMAT_FIELDS)
