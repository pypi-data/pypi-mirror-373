import os
from typing import Annotated

import typer
from humanize import naturaltime
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from linq.cli import get_custom_console
from linq.cli.cli_safe_linq_client import CliSafeLinq

from ..auth import client_auth
from ..client import Linq
from ..config import Config
from ..credentials import Credentials
from .utils import is_configured, is_logged_in

auth = typer.Typer(
    help="Authenticate with the LINQ API",
    invoke_without_command=True,
    no_args_is_help=True,
    callback=is_configured,
    name="auth",
)

credentials = typer.Typer(
    help="Manage stored machine credentials",
    invoke_without_command=True,
    no_args_is_help=True,
)
auth.add_typer(credentials, name="credentials", callback=is_logged_in)


@auth.command()
def login(
    machine: Annotated[
        bool,
        typer.Option(
            help="Use machine-to-machine authentication. Requires `LINQ_CLIENT_ID` and `LINQ_CLIENT_SECRET` environment variables to be set."
        ),
    ] = False,
) -> None:
    """Login to the LINQ API."""
    config = Config.load()
    console = get_custom_console()
    try:
        if machine:
            client_id = os.getenv("LINQ_CLIENT_ID", "")
            client_secret = os.getenv("LINQ_CLIENT_SECRET", "")
            if not client_id or not client_secret:
                raise typer.BadParameter(
                    "Machine-to-machine authentication credentials are not configured - please set `LINQ_CLIENT_ID` and `LINQ_CLIENT_SECRET` variables in your environment"
                )
            access_token, _ = client_auth.machine_login(
                client_id=client_id,
                client_secret=client_secret,
                auth0_domain=config.auth0_domain,
                customer_domain=config.domain,
            )
        else:
            access_token, _ = client_auth.login(
                client_id=config.client_id,
                auth0_domain=config.auth0_domain,
                customer_domain=config.domain,
            )

        credentials = Credentials(access_token=access_token)
        credentials.save()

        console.print("Login successful!", style="green")

    except client_auth.AuthError as e:
        console.print(f"Login failed - {e.message['error']}: {e.message['description']}", style="bold red")
        raise typer.Exit(1)


@credentials.command()
def list():
    """List machine credentials."""
    client = CliSafeLinq()
    console = get_custom_console()
    all_credentials = client.list_machine_credentials()
    tree = Tree("Machine Credentials", guide_style="dim")

    if not all_credentials:  # pragma: no cover
        console.print("No machine credentials found", style="yellow")
        return

    for credentials in all_credentials:
        tree.add(
            (
                f"ID: [bold]{credentials.client_id}[/bold], "
                f"Name: [bold]{credentials.name}[/], "
                f"Created At: [bold]{naturaltime(credentials.created_at) if credentials.created_at else '-'}[/], "
                f"Updated At: [bold]{naturaltime(credentials.updated_at) if credentials.updated_at else '-'}[/]"
            )
        )

    console.print(tree)


@credentials.command()
def create(name: Annotated[str, typer.Option(help="Name of the machine-to-machine authentication credentials.")]):
    """Create a new set of machine credentials used for SDK login in CI pipelines for example"""
    client = CliSafeLinq()
    credentials = client.create_machine_credentials(name=name)

    _print_secret(id=credentials.client_id, name=credentials.name, secret=credentials.client_secret)


@credentials.command()
def delete(id: Annotated[str, typer.Option(help="ID of the machine-to-machine authentication credentials.")]):
    """Delete machine credentials."""
    client = CliSafeLinq()
    console = get_custom_console()
    typer.confirm(f"Are you sure you want to delete machine credentials with ID `{id}`?", abort=True)

    client.delete_machine_credentials(id=id)

    console.print(f"Machine credentials with ID `{id}` deleted successfully", style="green")


@credentials.command()
def rotate_secret(id: Annotated[str, typer.Option(help="ID of the machine-to-machine authentication credentials.")]):
    """Rotate machine credentials secret"""
    client = CliSafeLinq()
    typer.confirm(
        (
            f"Are you sure you want to rotate the secret for this machine credentials with ID `{id}`? "
            "\nYou will have to update previous secrets after rotating."
        ),
        abort=True,
    )

    credentials = client.rotate_machine_credentials_secret(id=id)
    _print_secret(id=credentials.client_id, name=credentials.name, secret=credentials.client_secret)


def _print_secret(*, id: str, name: str, secret: str) -> None:
    console = get_custom_console()

    console.print(
        f"Machine credentials `{name}` with ID `{id}` rotated successfully",
        style="green",
    )
    console.line()
    console.print(
        Panel(
            Text(secret, style="bold blue"),
            title="Your new credentials secret is:",
            title_align="left",
            border_style="blue",
        )
    )
    console.print("Please save this secret securely, you will not be able to view it again!", style="bold yellow")
    console.print(
        "Be careful with who can access these credentials - using these credentials acts as the creator user, and they will stop working if the creator account is deleted.",
        style="bold yellow",
    )
