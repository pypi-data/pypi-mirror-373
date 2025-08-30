from globus_cli.parsing import group


@group(
    "create",
    short_help="Create a timer.",
    lazy_subcommands={"transfer": (".transfer", "transfer_command")},
)
def create_command() -> None:
    pass
