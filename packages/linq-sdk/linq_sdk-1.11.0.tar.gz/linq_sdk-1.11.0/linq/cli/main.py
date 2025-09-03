from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import Annotated
from uuid import UUID

import typer
from rich.console import Console
from rich.progress import Progress
from rich.prompt import Prompt
from rich.tree import Tree

from linq import __version__
from linq.cli import get_custom_console
from linq.cli.cli_safe_linq_client import CliSafeLinq
from linq.client import Linq
from linq.config import Config
from linq.utils import Download

from .auth import auth
from .driver import driver
from .scripts import scripts
from .workcell import workcell
from .workflow import workflow


def version_callback(version: Annotated[bool, typer.Option(help="Show the version and exit", is_eager=True)] = False):
    if version:
        console = Console(highlight=False)
        console.print(
            dedent(
                """
               ##           db    88   88 888888  dP"Yb  8b    d8    db    888888    db
                ##         dPYb   88   88   88   dP   Yb 88b  d88   dPYb     88     dPYb
             #     #      dP__Yb  Y8   8P   88   Yb   dP 88YbdP88  dP__Yb    88    dP__Yb
            ##    ###    dP    Yb `YbodP'   88    YbodP  88 YY 88 dP    Yb   88   dP    Yb
            """
            ),
            style="white",
        )

        client = CliSafeLinq()
        api_version = client.get_api_version()

        console.print(f"Automata LINQ SDK CLI: [bold cyan]{__version__}[/]")
        console.print(f"Automata LINQ WORKFLOW BUILDER API: [bold cyan]{api_version}[/]")
        raise typer.Exit()


cli = typer.Typer(
    name="linq",
    help="CLI for interacting with [cyan bold]Automata LINQ[/]\n",
    epilog="For more information, visit [cyan]https://docs.automata.tech[/]",
    short_help="CLI for Automata LINQ",
    invoke_without_command=True,
    no_args_is_help=True,
    rich_markup_mode="rich",
    pretty_exceptions_show_locals=False,
    callback=version_callback,
)


def _get_configuration_values(
    console: Console,
    existing_configuration: Config,
    domain: str | None = None,
    auth0_domain: str | None = None,
    client_id: str | None = None,
) -> Config:
    if domain is None:
        domain = (
            Prompt.ask(
                "Please enter your LINQ API domain "
                "(usually [cyan]api.<customer>.linq.cloud[/cyan] in single tenancy "
                "or just [cyan]api.linq.cloud[/cyan] for shared tenancy)",
                console=console,
                default=existing_configuration.domain or None,
            )
            or ""
        )

    if domain.startswith("http://"):
        domain = domain[7:]
    elif domain.startswith("https://"):
        domain = domain[8:]
    domain = domain.rstrip("/")

    if auth0_domain is None:
        auth0_domain = (
            Prompt.ask(
                "Please enter your auth0 domain",
                console=console,
                default=existing_configuration.auth0_domain or None,
            )
            or ""
        )

    if auth0_domain.startswith("http://"):
        auth0_domain = auth0_domain[7:]
    elif auth0_domain.startswith("https://"):
        auth0_domain = auth0_domain[8:]
    auth0_domain = auth0_domain.rstrip("/")

    if client_id is None:
        client_id = (
            Prompt.ask(
                "Please enter your Client ID (a 32 character alphanumeric string)",
                console=console,
                default=existing_configuration.client_id or None,
            )
            or ""
        )

    return Config(
        domain=domain,
        client_id=client_id,
        auth0_domain=auth0_domain,
    )


@cli.command()
def configure(
    domain: Annotated[
        str | None,
        typer.Option(
            help="The LINQ API domain (usually [cyan]api.<customer>.linq.cloud[/cyan] in single tenancy or just [cyan]api.linq.cloud[/cyan] for shared tenancy)"
        ),
    ] = None,
    auth0_domain: Annotated[str | None, typer.Option(help="The Auth0 domain")] = None,
    client_id: Annotated[str | None, typer.Option(help="The Auth0 client ID")] = None,
    clear: Annotated[bool, typer.Option(help="Clear the current configuration", is_eager=True)] = False,
):
    """Configure the CLI for your Automata LINQ environment."""
    console = Console()

    if clear:
        Config.delete()
        console.print("Configuration data deleted. Run [green]linq configure[/green] to reconfigure the CLI.")
        raise typer.Exit(0)

    all_correct = False
    configuration_values = None
    while not all_correct:
        console.print()
        configuration_values = _get_configuration_values(
            console, existing_configuration=Config.load(), domain=domain, auth0_domain=auth0_domain, client_id=client_id
        )
        console.print()
        console.print(f"API domain: [bold cyan]{configuration_values.domain}[/bold cyan]")
        console.print(f"Auth0 domain: [bold cyan]{configuration_values.auth0_domain}[/bold cyan]")
        console.print(f"Client ID: [bold cyan]{configuration_values.client_id}[/bold cyan]")
        all_correct = (domain and auth0_domain and client_id) or (
            Prompt.ask("Are these details correct?", choices=["y", "n"]) == "y"
        )
    assert configuration_values
    configuration_values.save()


@cli.command()
def scheduler_versions(
    scheduler: Annotated[str | None, typer.Option(help="The name of the scheduler to get versions for")] = None,
):
    """Get a list of supported versions for a given scheduler, defaults to all schedulers."""
    console = get_custom_console()
    client = CliSafeLinq()

    result = client.get_supported_scheduler_versions()

    if scheduler is not None:
        for version in result.get(scheduler, []):
            print(version)
    else:
        console.print("LINQ API scheduler versions", style="underline")
        tree = Tree("Versions", hide_root=True, guide_style="dim")

        for scheduler, versions in result.items():
            scheduler_branch = tree.add(scheduler)
            for version in versions:
                scheduler_branch.add(version)

        console.print(tree)


@cli.command()
def export_run_logs(
    workcell_id: Annotated[UUID, typer.Option(help="ID of the workcell to export logs from", dir_okay=True)],
    from_date: Annotated[datetime, typer.Option(help="Start date to export logs from")],
    output_dir: Annotated[Path, typer.Option(help="Path to the directory to save the logs to", exists=False)],
):
    """Export logs for a given workcell to a directory."""
    client = CliSafeLinq()

    runs = client.get_run_histories(
        device_id=workcell_id,
        start=from_date,
        order="ascending",
        count=1000,
    )
    num_runs = len(runs.list)
    with Progress() as progress:
        export_task = progress.add_task(f"Exporting {num_runs} run logs", total=num_runs)

        for run in runs.list:
            task = progress.add_task(f"Exporting logs for run {run.id}", total=1)
            export_url = client.export_run_logs(run.id)
            with Download(url=export_url, output_dir=output_dir) as download:
                for download_progress in download.transfer_with_progress():
                    progress.update(task, completed=download_progress)

            progress.update(export_task, advance=1)


cli.add_typer(driver, name="driver")
cli.add_typer(workflow, name="workflow")
cli.add_typer(scripts, name="scripts")
cli.add_typer(workcell, name="workcell")
cli.add_typer(auth, name="auth")

if __name__ == "__main__":
    cli()
