from itertools import groupby
from operator import attrgetter
from typing import Annotated

import typer
from rich.markup import escape
from rich.tree import Tree

from linq.cli import get_custom_console
from linq.cli.cli_safe_linq_client import CliSafeLinq
from linq.client import Linq
from linq.schema.workflow_api import Argument, DataOutputInfo, Driver
from linq.utils import get_latest_scheduler_version

from .utils import is_configured_and_logged_in

driver = typer.Typer(
    help="Explore driver configuration and capabilities",
    invoke_without_command=True,
    no_args_is_help=True,
    callback=is_configured_and_logged_in,
)


def render_argument(tree: Tree, argument_name: str, argument: Argument):
    argument_type = argument.type
    if isinstance(argument_type, str):
        tree.add(f"{argument_name}: {argument_type}")
    elif isinstance(argument_type, list):
        list_representation = f"[{argument_type[0]}]"
        tree.add(f"{argument_name}: {escape(list_representation)}")
    elif isinstance(argument_type, dict):
        argument_branch = tree.add(argument_name)
        for nested_argument_name, nested_argument in argument_type.items():
            render_argument(argument_branch, nested_argument_name, nested_argument)
    else:
        raise RuntimeError(f"Unknown argument type {argument_type}")  # pragma: no cover


def render_data_output(tree: Tree, output_info: DataOutputInfo):
    if output_info.suffix_with_field:
        suffix_str = f"_<{output_info.suffix_with_field.field_name}>"
        if output_info.suffix_with_field.repeated_field:
            suffix_str += f" (for each entry in {output_info.suffix_with_field.field_name})"
    else:
        suffix_str = ""
    if output_info.type is None:
        output_type = "unknown"
    else:
        output_type = output_info.type

    tree.add(f"{output_info.name}{suffix_str}: [italic]{output_type}[/italic]")


def result_matches(result: Driver, *, name: str | None, version: str | None, search: str | None):
    if name is not None and result.name != name:
        return False
    if version is not None and result.version != version:
        return False
    if search is not None and search.lower() not in result.name.lower():
        return False
    return True


@driver.command(name="list")
def list_drivers(
    scheduler_version: Annotated[str | None, typer.Option(help="Scheduler version to get drivers from")] = None,
    name: Annotated[str | None, typer.Option(help="Exact name of driver")] = None,
    version: Annotated[str | None, typer.Option(help="Exact version of driver")] = None,
    search: Annotated[str | None, typer.Option(help="Search for partial name of driver")] = None,
    names_only: Annotated[bool, typer.Option(help="Only show driver names, no configuration options")] = False,
):
    """List all drivers, and each of their actions, for the specified scheduler version."""
    console = get_custom_console()
    client = CliSafeLinq()

    if scheduler_version is None:
        scheduler_version = get_latest_scheduler_version()

    try:
        drivers = [
            meta
            for meta in client.get_all_drivers(scheduler="maestro", version=scheduler_version)
            if result_matches(meta, name=name, version=version, search=search)
        ]

    except Exception as e:  # pragma no coverage
        console.print(str(e), style="red")
        raise typer.Exit(1)

    if not len(drivers):
        console.print("[red]No matching drivers found.[/red]")
        return

    # Sort the drivers (first by name, then version, so they can be grouped)
    drivers = sorted(drivers, key=attrgetter("name", "version"))
    grouped_drivers = groupby(drivers, key=attrgetter("name"))

    tree = Tree(f"[green]Drivers for scheduler version {scheduler_version}[/green]", hide_root=False, guide_style="dim")

    for driver_name, driver_versions in grouped_drivers:
        driver_versions = list(driver_versions)
        has_single_version = len(driver_versions) == 1

        driver_name_with_search = (
            driver_name.replace(search.lower(), f"[underline]{search.lower()}[/underline]") if search else driver_name
        )

        driver_header = f"[bold]{driver_name_with_search}[/bold]"
        if has_single_version:
            # For single versions, avoid adding an extra layer of nesting
            driver_header = f"{driver_header} ({driver_versions[0].version})"
        driver_branch = tree.add(driver_header)

        for driver_version in driver_versions:
            if has_single_version:
                version_branch = driver_branch
            else:
                version_branch = driver_branch.add(f"[bold]{driver_version.version}[/bold]")
            if not names_only:
                config_branch = version_branch.add("[bold]Configuration[/bold]")
                for option_name, option_argument in driver_version.configuration.items():
                    render_argument(config_branch, option_name, option_argument)
                    # config_branch.add(f"{config_option_name} {config_option_arguments}")  # needs recursion

                actions_branch = version_branch.add("[bold]Actions[/bold]")
                for action_name, action in driver_version.actions.items():
                    action_branch = actions_branch.add(f"[bold]{action_name}[/bold]")
                    if action.arguments:
                        parameters_branch = action_branch.add("[bold]Arguments[/bold]")
                        for option_name, option_argument in action.arguments.items():
                            render_argument(parameters_branch, option_name, option_argument)
                    if action.data_outputs:
                        data_outputs_branch = action_branch.add("[bold]Data Outputs[/bold]")
                        for output_argument in action.data_outputs.values():
                            render_data_output(data_outputs_branch, output_argument)
                    # action_branch.add(f"{action_name} {action_arguments}")  # needs recursion
    console.print(tree)
