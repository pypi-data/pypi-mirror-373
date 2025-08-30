from globus_cli.parsing import group


@group(
    "role",
    lazy_subcommands={
        "list": (".list", "list_command"),
        "show": (".show", "show_command"),
    },
)
def role_command() -> None:
    """Manage Roles on Collections."""
