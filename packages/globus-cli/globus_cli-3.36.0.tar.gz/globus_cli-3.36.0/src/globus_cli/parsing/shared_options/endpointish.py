from __future__ import annotations

import typing as t

import click

from globus_cli import utils
from globus_cli.parsing.mutex_group import MutexInfo, mutex_option_group
from globus_cli.parsing.param_types import (
    CommaDelimitedList,
    LocationType,
    StringOrNull,
    UrlOrNull,
)
from globus_cli.types import AnyCommand

C = t.TypeVar("C", bound=AnyCommand)


_GCSONLY = "(Globus Connect Server only)"
_MANAGEDONLY = "(Managed endpoints only)"


class endpointish_params:
    """
    This helper provides arguments and options for "endpointish" entity types.

    It translates "high level" options which describe the operation being performed into
    "low level" options which describe the behavior which is appropriate.
    """

    @classmethod
    def create(
        cls,
        *,
        name: t.Literal["endpoint", "collection"],
        display_name_style: t.Literal["argument", "option"] = "argument",
        keyword_style: t.Literal["string", "list"] = "list",
        verify_style: t.Literal["flag", "choice"] = "choice",
        add_legacy_params: bool = False,
        skip: tuple[str, ...] = (),
    ) -> t.Callable[[C], C]:
        def decorator(f: C) -> C:
            return _apply_endpointish_create_or_update_params(
                f,
                name,
                display_name_style=display_name_style,
                keyword_style=keyword_style,
                verify_style=verify_style,
                add_legacy_params=add_legacy_params,
                skip=skip,
            )

        return decorator

    @classmethod
    def update(
        cls,
        *,
        name: t.Literal["endpoint", "collection"],
        display_name_style: t.Literal["argument", "option"] = "option",
        keyword_style: t.Literal["string", "list"] = "list",
        verify_style: t.Literal["flag", "choice"] = "choice",
        add_legacy_params: bool = False,
        skip: tuple[str, ...] = (),
    ) -> t.Callable[[C], C]:
        def decorator(f: C) -> C:
            return _apply_endpointish_create_or_update_params(
                f,
                name,
                display_name_style=display_name_style,
                keyword_style=keyword_style,
                verify_style=verify_style,
                public_default=None,
                add_legacy_params=add_legacy_params,
                skip=skip,
            )

        return decorator


def _apply_endpointish_create_or_update_params(
    f: C,
    name: t.Literal["endpoint", "collection"],
    *,
    public_default: bool | None = True,
    display_name_style: str,
    keyword_style: str,
    verify_style: str,
    add_legacy_params: bool,
    skip: tuple[str, ...] = (),
) -> C:
    decorators: dict[str, t.Callable[[C], C]] = {}

    if display_name_style == "argument":
        decorators["display_name"] = click.argument("DISPLAY_NAME")
    elif display_name_style == "option":
        decorators["display_name"] = click.option(
            "--display-name", help=f"Name for the {name}"
        )
    else:
        raise NotImplementedError()

    decorators.update(
        {
            "description": click.option(
                "--description", help=f"Description for the {name}", type=StringOrNull()
            ),
            "info_link": click.option(
                "--info-link",
                help=f"Link for info about the {name}",
                type=StringOrNull(),
            ),
            "contact_info": click.option(
                "--contact-info",
                help=f"Contact info for the {name}",
                type=StringOrNull(),
            ),
            "contact_email": click.option(
                "--contact-email",
                help=f"Contact email for the {name}",
                type=StringOrNull(),
            ),
            "organization": click.option(
                "--organization",
                help=f"Organization for the {name}",
                type=StringOrNull(),
            ),
            "department": click.option(
                "--department",
                help=f"Department which operates the {name}",
                type=StringOrNull(),
            ),
            "keywords": click.option(
                "--keywords",
                type=str if keyword_style == "string" else CommaDelimitedList(),
                help=(
                    f"Comma separated list of keywords to help searches for the {name}"
                ),
            ),
            "default_directory": click.option(
                "--default-directory",
                type=StringOrNull(),
                help=(
                    f"Default directory when browsing or executing tasks on the {name}"
                ),
            ),
            "force_encryption": click.option(
                "--force-encryption/--no-force-encryption",
                default=None,
                help=f"Force the {name} to encrypt transfers",
            ),
            "user_message": click.option(
                "--user-message",
                help=(
                    "A message for clients to display to users when interacting "
                    f"with this {name}"
                ),
                type=StringOrNull(),
            ),
            "user_message_link": click.option(
                "--user-message-link",
                help=(
                    "Link to additional messaging for clients to display to users "
                    f"when interacting with this {name}. "
                    "Should be an HTTP or HTTPS URL "
                ),
                type=UrlOrNull(),
            ),
            "public": click.option(
                "--public/--private",
                is_flag=True,
                default=public_default,
                help=(
                    f"Set the {name} to be public or private."
                    + (f" {_GCSONLY}" if add_legacy_params else "")
                ),
            ),
        }
    )

    if verify_style == "choice":
        verify_help = (
            f"Set the policy for this {name} for file integrity verification "
            "after transfer. 'force' requires all transfers to perform "
            "verification. 'disable' disables all verification checks. 'default' "
            "allows the user to decide on verification at Transfer task submit  "
            "time."
        )
        if name == "collection":
            verify_help += (
                " When set on mapped collections, this policy is inherited by any "
                "guest collections"
            )
        decorators["verify"] = click.option(
            "--verify",
            type=click.Choice(["force", "disable", "default"], case_sensitive=False),
            callback=_verify_choice_to_dict,
            help=verify_help,
        )
    else:
        decorators["verify"] = click.option(
            "--disable-verify/--no-disable-verify",
            default=None,
            is_flag=True,
            help=f"Set the {name} to ignore checksum verification",
        )

    decorator_list = [v for k, v in decorators.items() if k not in skip]

    if add_legacy_params:
        decorator_list.extend(_LEGACY_TRANSFER_PARAMS)

    return utils.fold_decorators(f, decorator_list)


def _verify_choice_to_dict(
    ctx: click.Context, param: click.Parameter, value: t.Any
) -> dict[str, bool]:
    if value is None:
        return {}
    value = value.lower()
    return {"force_verify": value == "force", "disable_verify": value == "disable"}


_endpoint_activation_params = [
    click.option("--myproxy-dn", help=f"Set the MyProxy Server DN {_GCSONLY}"),
    click.option("--myproxy-server", help=f"Set the MyProxy Server URI {_GCSONLY}"),
    click.option("--oauth-server", help=f"Set the OAuth Server URI {_GCSONLY}"),
]

_endpoint_subscription_params = [
    click.option(
        "--managed",
        "managed",
        is_flag=True,
        flag_value=True,
        default=None,
        help=(
            "Set the endpoint as a managed endpoint. Requires the "
            "user to be a subscription manager. If the user has "
            "multiple subscription IDs, --subscription-id must be used "
            "instead"
        ),
    ),
    click.option(
        "--no-managed",
        "managed",
        is_flag=True,
        flag_value=False,
        default=None,
        help=(
            "Unset the endpoint as a managed endpoint. "
            "Does not require the user to be a subscription manager. "
            "Mutually exclusive with --subscription-id"
        ),
    ),
    click.option(
        "--subscription-id",
        type=click.UUID,
        default=None,
        help=(
            "Set the endpoint as a managed endpoint with the given subscription ID. "
            "Mutually exclusive with --no-managed"
        ),
    ),
    mutex_option_group(
        "--subscription-id",
        MutexInfo(
            "--no-managed", param="managed", present=lambda d: d.get("managed") is False
        ),
    ),
]

_endpoint_network_use_params = [
    click.option(
        "--network-use",
        default=None,
        type=click.Choice(["normal", "minimal", "aggressive", "custom"]),
        help=(
            "Set the endpoint's network use level. If using custom, "
            "the endpoint's max and preferred concurrency and "
            f"parallelism must be set {_MANAGEDONLY} {_GCSONLY}"
        ),
    ),
    click.option(
        "--max-concurrency",
        type=int,
        default=None,
        help=(
            "Set the endpoint's max concurrency; "
            f"requires --network-use=custom {_MANAGEDONLY} {_GCSONLY}"
        ),
    ),
    click.option(
        "--preferred-concurrency",
        type=int,
        default=None,
        help=(
            "Set the endpoint's preferred concurrency; "
            f"requires --network-use=custom {_MANAGEDONLY} {_GCSONLY}"
        ),
    ),
    click.option(
        "--max-parallelism",
        type=int,
        default=None,
        help=(
            "Set the endpoint's max parallelism; "
            f"requires --network-use=custom {_MANAGEDONLY} {_GCSONLY}"
        ),
    ),
    click.option(
        "--preferred-parallelism",
        type=int,
        default=None,
        help=(
            "Set the endpoint's preferred parallelism; "
            f"requires --network-use=custom {_MANAGEDONLY} {_GCSONLY}"
        ),
    ),
]

_location_option = click.option(
    "--location",
    type=LocationType(),
    default=None,
    help=f"Manually set the endpoint's latitude and longitude {_GCSONLY}",
)


_LEGACY_TRANSFER_PARAMS = (
    [_location_option]
    + _endpoint_network_use_params
    + _endpoint_activation_params
    + _endpoint_subscription_params
)
