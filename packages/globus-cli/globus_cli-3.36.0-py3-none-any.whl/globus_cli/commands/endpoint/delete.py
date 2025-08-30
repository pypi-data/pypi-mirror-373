import uuid

from globus_cli.endpointish import Endpointish
from globus_cli.login_manager import LoginManager
from globus_cli.parsing import command, endpoint_id_arg
from globus_cli.termio import display


@command(
    "delete",
    short_help="Delete an endpoint.",
    adoc_examples="""[source,bash]
----
$ ep_id=aa752cea-8222-5bc8-acd9-555b090c0ccb
$ globus endpoint delete $ep_id
----
""",
)
@endpoint_id_arg
@LoginManager.requires_login("transfer")
def endpoint_delete(login_manager: LoginManager, *, endpoint_id: uuid.UUID) -> None:
    """Delete a given endpoint.

    WARNING: Deleting an endpoint will permanently disable any existing shared
    endpoints that are hosted on it.
    """
    transfer_client = login_manager.get_transfer_client()
    Endpointish(
        endpoint_id, transfer_client=transfer_client
    ).assert_is_traditional_endpoint()

    res = transfer_client.delete_endpoint(endpoint_id)
    display(res, text_mode=display.RAW, response_key="message")
