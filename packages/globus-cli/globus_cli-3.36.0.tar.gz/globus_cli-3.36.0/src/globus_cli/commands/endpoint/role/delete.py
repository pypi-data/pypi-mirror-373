import uuid

from globus_cli.login_manager import LoginManager
from globus_cli.parsing import command, endpoint_id_arg
from globus_cli.termio import display

from ._common import role_id_arg


@command(
    "delete",
    short_help="Remove a role from an endpoint.",
    adoc_output="Textual output is a simple success message in the absence of errors.",
    adoc_examples="""Delete role '0f007eec-1aeb-11e7-aec4-3c970e0c9cc4' on endpoint
'aa752cea-8222-5bc8-acd9-555b090c0ccb':

[source,bash]
----
$ globus endpoint role delete 'aa752cea-8222-5bc8-acd9-555b090c0ccb' \
    '0f007eec-1aeb-11e7-aec4-3c970e0c9cc4'
----
""",
)
@endpoint_id_arg
@role_id_arg
@LoginManager.requires_login("transfer")
def role_delete(
    login_manager: LoginManager, *, role_id: str, endpoint_id: uuid.UUID
) -> None:
    """
    Remove a role from an endpoint.

    You must have sufficient privileges to modify the roles on the endpoint.
    """
    transfer_client = login_manager.get_transfer_client()
    res = transfer_client.delete_endpoint_role(endpoint_id, role_id)
    display(res, text_mode=display.RAW, response_key="message")
