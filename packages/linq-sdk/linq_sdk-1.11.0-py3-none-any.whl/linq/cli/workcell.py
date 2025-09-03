import json
import time
from pathlib import Path
from typing import Annotated, Any
from uuid import UUID

import humanize.time
import typer
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from linq._internal.client import InternalLinq
from linq.cli import get_custom_console
from linq.cli.cli_safe_linq_client import CliSafeLinq
from linq.client import REASON_NOT_REQUIRED
from linq.credentials import Credentials
from linq.exceptions import HubRestartCommandResponseNotFound
from linq.schema import backend_api

from .utils import is_configured_and_logged_in

workcell = typer.Typer(
    help="Deploy to and control your workcells",
    invoke_without_command=True,
    no_args_is_help=True,
    callback=is_configured_and_logged_in,
)

error = typer.Typer(
    help="Respond to errors on your workcells",
    invoke_without_command=True,
    no_args_is_help=True,
    callback=is_configured_and_logged_in,
)
workcell.add_typer(error, name="error")


def _import_transport_config(path: Path, console: Console) -> dict[str, Any] | None:
    "Import transport config from a json file"
    try:
        with open(path, "r") as f:
            transport_config = json.load(f)
        return transport_config
    except FileNotFoundError:
        console.print(f"Error: The file at {path} was not found.", style="red")
    except json.JSONDecodeError:
        console.print(f"Error: The file at {path} is not a valid JSON.", style="red")
    except Exception as e:
        console.print(f"An unexpected error occurred: {e}", style="red")


@workcell.command()
def deploy(
    workflow_id: Annotated[UUID, typer.Option(help="The ID of the workflow to deploy")],
    workcell_id: Annotated[UUID, typer.Option(help="The ID of the workcell to deploy the workflow to")],
    reason: Annotated[str | None, typer.Option(help="Reason for deploying the workflow")] = None,
):
    """Deploy a workflow to hub on related workcell."""
    console = get_custom_console()
    client = CliSafeLinq()

    client.deploy_workflow(
        workflow_id=workflow_id,
        device_id=workcell_id,
        reason=reason or REASON_NOT_REQUIRED,
    )

    console.print(f"Workflow {workflow_id} deployed to workcell {workcell_id} successfully", style="green")


@workcell.command()
def start(
    workcell_id: Annotated[UUID, typer.Option(help="ID of the workcell whose workflow should be started.")],
    reason: Annotated[str | None, typer.Option(help="Reason for starting the workflow")] = None,
):
    """Start the currently deployed workflow on hub of the given workcell."""
    console = get_custom_console()
    client = CliSafeLinq()

    client.start_workflow(device_id=workcell_id, reason=reason or REASON_NOT_REQUIRED)

    console.print(f"Workflow started on workcell {workcell_id} successfully", style="green")


@workcell.command()
def status(workcell_id: Annotated[UUID, typer.Option(help="ID of the workcell to get the status of.")]):
    """Get the status of the currently deployed workflow on hub of the given workcell."""
    console = get_custom_console()
    client = CliSafeLinq()
    data = client.get_status(device_id=str(workcell_id))

    console.print(f"Status: [bold]{data.status.upper()}[/], Details: [bold]{data.details if data.details else '-'}[/]")


@workcell.command(hidden=True)
def transport_config(
    workcell_id: Annotated[str, typer.Option(help="ID of the workcell to get the transport config of.")],
):
    """Get the transport config for a given workcell."""
    console = get_custom_console()
    client = InternalLinq()
    data = client.get_workcell_transport_config(workcell_id)

    console.print(data, style="green")


@workcell.command(hidden=True)
def upload_transport_config(
    path: Annotated[Path, typer.Argument(help="File path to the python file with the workflow object")],
):
    """Get the transport config for given workcell."""
    console = get_custom_console()
    client = InternalLinq()
    transport_config = _import_transport_config(path, console)
    if not transport_config:
        raise typer.Exit(1)
    data = client.post_workcell_transport_config(transport_config)

    console.print(data["id"], style="green")


@error.command()
def get_latest(workcell_id: Annotated[UUID, typer.Option(help="ID of the workcell to get the latest error of.")]):
    """Get the latest error of the currently deployed workflow on hub of the given workcell."""
    console = get_custom_console()
    client = CliSafeLinq()
    data = client.get_latest_error(device_id_or_serial=workcell_id)

    if not data:
        console.print("No errors found", style="green")
        raise typer.Exit(0)

    tree = Tree(Text(f"Error! {data.error_message}", style="red bold"), guide_style="dim")
    tree.add(f"Error ID: {data.id}")
    tree.add(f"Error Code: {data.error_code}")
    tree.add(f"Severity: {data.error_severity.upper()}")
    tree.add(f"Instrument: {data.instrument.name} ({data.instrument.id})")
    tree.add(f"Time Stamp: {humanize.naturaltime(data.timestamp)}")
    tree.add(f"Available Actions: {', '.join([a.value for a in data.available_actions])}")
    console.print(tree)


@error.command()
def respond(
    workcell_id: Annotated[UUID, typer.Option(help="ID of the workcell to reset.")],
    error_id: Annotated[UUID, typer.Option(help="ID of the error to respond to.")],
    action: Annotated[backend_api.DeviceErrorAvailableActions, typer.Option(help="Action to take on the error.")],
):
    """Respond to an error on hub of the given workcell."""
    console = get_custom_console()
    client = CliSafeLinq()

    action = backend_api.DeviceErrorAvailableActions(action)

    latest_error = client.get_latest_error(device_id_or_serial=workcell_id)
    if not latest_error:
        console.print(f"No errors found on workcell {workcell_id}", style="red")
        raise typer.Exit(1)
    if latest_error.id != error_id:
        # Need to check what actions are available
        console.print(f"Error {error_id} not found on workcell {workcell_id}", style="red")
        raise typer.Exit(1)

    if action not in latest_error.available_actions:
        console.print(f"Action {action.value} is not available for error {error_id}", style="red")
        raise typer.Exit(1)

    if action == backend_api.DeviceErrorAvailableActions.AbortLabware:
        confirmed = _abort_labware_confirmation(latest_error.labware_affected_by_abort, console)
        if not confirmed:
            console.print("Cancelling abort-labware action", style="orange1")
            raise typer.Exit(1)

    client.respond_to_error(
        device_id=workcell_id,
        error_id=error_id,
        action=action,
    )

    console.print(
        f"Responded to error {error_id} on workcell {workcell_id} with action {action.value} successfully",
        style="green",
    )


def _abort_labware_confirmation(
    affected_labware: list[backend_api.DeviceErrorAffectedLabware],
    console: Console,
) -> bool:
    _print_abort_labware_affected_labware(affected_labware, console)
    return Confirm.ask(
        prompt=Text(
            "Remove the labware from the workcell and then chose confirm, or chose cancel",
            style="orange1 bold",
        ),
        choices=["confirm", "cancel"],
        console=console,
    )


def _print_abort_labware_affected_labware(
    affected_labware: list[backend_api.DeviceErrorAffectedLabware],
    console: Console,
) -> None:
    table = Table(
        "Labware ID",
        "Reason",
        "Current Location",
        show_header=True,
        header_style="bold",
    )
    for labware in affected_labware:
        table.add_row(
            labware.labware_id,
            labware.reason,
            f"{labware.current_location.instrument_id}, slot {labware.current_location.slot}",
        )

    console.print("The following labware will be affected by the abort-labware action:", style="orange1")
    console.print(table)


@workcell.command()
def pause(
    workcell_id: Annotated[UUID, typer.Option(help="ID of the workcell the workflow is currently running on.")],
    reason: Annotated[str | None, typer.Option(help="Reason for pausing the workflow")] = None,
):
    """Pause the currently deployed workflow on hub of the given workcell."""
    console = get_custom_console()
    client = CliSafeLinq()
    client.pause_workflow(device_id=workcell_id, reason=reason or REASON_NOT_REQUIRED)

    console.print(f"Workflow paused on workcell {workcell_id} successfully", style="green")


@workcell.command()
def resume(
    workcell_id: Annotated[UUID, typer.Option(help="ID of the workcell the workflow is currently running (paused) on")],
    reason: Annotated[str | None, typer.Option(help="Reason for resuming the workflow")] = None,
):
    """Resume the currently deployed workflow on hub of the given workcell."""
    console = get_custom_console()
    client = CliSafeLinq()

    client.resume_workflow(device_id=workcell_id, reason=reason or REASON_NOT_REQUIRED)

    console.print(f"Workflow resumed on workcell {workcell_id} successfully", style="green")


@workcell.command()
def stop(
    workcell_id: Annotated[UUID, typer.Option(help="ID of the workcell the workflow is currently running on.")],
    reason: Annotated[str | None, typer.Option(help="Reason for stopping the workflow")] = None,
):
    """Stop the currently deployed workflow on hub of the given workcell."""
    console = get_custom_console()
    client = CliSafeLinq()
    client.stop_workflow(device_id=workcell_id, reason=reason or REASON_NOT_REQUIRED)

    console.print(f"Workflow stopped on workcell {workcell_id} successfully", style="green")


@workcell.command()
def reset(
    workcell_id: Annotated[UUID, typer.Option(help="The ID of the workcell to reset")],
    reason: Annotated[str | None, typer.Option(help="Reason for resetting the workflow")] = None,
):
    """Reset the workflow currently deployed to hub of the given workcell."""
    console = get_custom_console()
    client = CliSafeLinq()
    client.reset_workflow(device_id=workcell_id, reason=reason or REASON_NOT_REQUIRED)

    console.print(f"Workflow reset on workcell {workcell_id} successfully", style="green")


@workcell.command()
def list(
    max_entries: Annotated[int, typer.Option(help="Maximum number of entries to display")] = 15,
):
    """Get a list of all workcells."""
    console = get_custom_console()
    client = CliSafeLinq()
    credentials: Credentials = Credentials.load()
    current_org_auth0_id = credentials.current_org_auth0_id()

    orgs = client.get_organizations()

    if not orgs:  # pragma: no cover
        console.print("No organizations found", style="yellow")
        raise typer.Exit(0)

    org = next((o for o in orgs if o.externalID == current_org_auth0_id), None)

    if org is None:  # pragma: no cover
        console.print("Authenticated org not found", style="yellow")
        raise typer.Exit(1)

    workcells = client.get_workcells(org.workspace)

    if not workcells:  # pragma: no cover
        console.print("No workcells found", style="yellow")
        raise typer.Exit(0)

    table = Table(title=f"Workcells in Organisation '{org.slug}'", show_header=True, header_style="bold")
    table.add_column("Name", max_width=60)
    table.add_column("Hub ID", min_width=36, no_wrap=True)
    table.add_column("Mode")
    table.add_column("Status")
    table.add_column("Last Access")

    status_colors = {
        backend_api.WorkcellStatus.READY: "green",
        backend_api.WorkcellStatus.RUNNING: "blue",
        backend_api.WorkcellStatus.OFFLINE: "red",
        backend_api.WorkcellStatus.ERROR: "red",
        backend_api.WorkcellStatus.BUSY: "amber",
    }

    for workcell in reversed(workcells[:max_entries]):
        table.add_row(
            workcell.name,
            str(workcell.hub_id),
            workcell.mode,
            Text(workcell.status, style=status_colors.get(workcell.status, "grey")),
            humanize.time.naturaltime(workcell.hub_last_access),
        )

    console.print(table)


@workcell.command()
def restart_hub_runtime(
    hub_serial: Annotated[str, typer.Option(help="ID of the hub-xxxxxx to restart runtime for.")],
):
    """Restart the hub runtime"""
    console = get_custom_console()
    client = CliSafeLinq()
    command_id = client.restart_hub_runtime(hub_serial=hub_serial)
    console.print(f"Restart command initiated for hub {hub_serial}", style="blue")

    backoff_time = 1
    max_backoff = 30
    retries = 0
    max_retries = 5

    with console.status("[blue]Restarting hub runtime..."):
        while True:
            try:
                result = client.get_restart_command_status(command_id=command_id)
            except HubRestartCommandResponseNotFound:
                if retries >= max_retries:
                    console.print(
                        (
                            f"Failed to get status of command '{command_id}' after {max_retries} retries."
                            " - possibly an unknown hub serial"
                        ),
                        style="red",
                    )
                    raise typer.Exit(1)
                retries += 1
                time.sleep(backoff_time)
                continue

            command_status = result.status

            match command_status:
                case "Pending":
                    console.print("Restart pending...", style="yellow")
                    time.sleep(backoff_time)
                case "InProgress":
                    console.print("Restart in progress...", style="yellow")
                    time.sleep(backoff_time)
                case "Success":
                    console.print(f"Hub runtime for {hub_serial} restarted successfully", style="green")
                    return
                case _:
                    console.print(
                        f"Command execution finished with {command_status} status "
                        f"on {result.instance_name if result.instance_name else 'unknown'} instance",
                        style="red",
                    )
                    console.print(f"StatusDetail: {result.status_details}", style="red")
                    raise typer.Exit(1)

            backoff_time = min(backoff_time * 2, max_backoff)
