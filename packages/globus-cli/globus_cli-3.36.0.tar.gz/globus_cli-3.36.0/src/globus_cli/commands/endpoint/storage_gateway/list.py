import uuid

from globus_cli.login_manager import LoginManager
from globus_cli.parsing import command, endpoint_id_arg
from globus_cli.termio import Field, display, formatters

STANDARD_FIELDS = [
    Field("ID", "id"),
    Field("Display Name", "display_name"),
    Field("High Assurance", "high_assurance"),
    Field("Allowed Domains", "allowed_domains", formatter=formatters.SortedArray),
]


@command("list", short_help="List the Storage Gateways on an Endpoint.")
@endpoint_id_arg
@LoginManager.requires_login("auth", "transfer")
def storage_gateway_list(
    login_manager: LoginManager,
    *,
    endpoint_id: uuid.UUID,
) -> None:
    """
    List the Storage Gateways on a given Globus Connect Server v5 Endpoint.
    """
    gcs_client = login_manager.get_gcs_client(endpoint_id=endpoint_id)
    res = gcs_client.get_storage_gateway_list()
    display(res, text_mode=display.TABLE, fields=STANDARD_FIELDS)
