from globus_cli.parsing import group


@group(
    "create",
    lazy_subcommands={
        "guest": (".guest", "collection_create_guest"),
        "mapped": (".mapped", "collection_create_mapped"),
    },
)
def collection_create() -> None:
    """Create a new Collection."""
