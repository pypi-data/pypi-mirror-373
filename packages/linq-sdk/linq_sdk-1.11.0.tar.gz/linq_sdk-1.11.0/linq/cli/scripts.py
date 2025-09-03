from typing import Annotated

import typer
from rich.tree import Tree

from linq.cli import get_custom_console
from linq.cli.cli_safe_linq_client import CliSafeLinq

from .utils import is_configured_and_logged_in

scripts = typer.Typer(
    help="Explore scripts that can be used in CodeTasks.",
    invoke_without_command=True,
    no_args_is_help=True,
    callback=is_configured_and_logged_in,
)


@scripts.command()
def info(
    version: Annotated[
        str | None,
        typer.Option(
            help="Version of the scripts to get information about. If not provided, the latest version will be used."
        ),
    ] = None,
):
    """Get information about the available CodeTask scripts."""
    client = CliSafeLinq()
    console = get_custom_console()
    scripts_info = client.get_scripts_info(version)

    tree = Tree(
        f"[green]Available Scripts for {scripts_info.org_slug} ({scripts_info.version})[/green]", guide_style="dim"
    )
    for script in scripts_info.functions:
        script_branch = tree.add(f"[bold]{script.function_name}[/bold]")
        script_branch.add(f"Description: {script.description}")
        inputs_branch = script_branch.add("[bold]Inputs[/bold]")
        if not script.arguments:
            inputs_branch.add("None")
        for input in script.arguments:
            input_str = f"{input.name}: [italic]{input.type}[/italic]"
            if input.default:
                input_str += f" (default={input.default})"
            inputs_branch.add(input_str)
        returns_branch = script_branch.add("[bold]Returns[/bold]")
        if not script.returns:
            returns_branch.add("None")
        for ret in script.returns:
            returns_branch.add(f"{ret.name}: [italic]{ret.type}[italic]")

    console.print(tree)


@scripts.command()
def list_versions():
    """List all available scripts package versions"""
    client = CliSafeLinq()
    console = get_custom_console()
    scripts = client.list_scripts_versions()

    console.print("[bold]Available scripts package versions:[/bold]")
    for script in scripts:
        console.print(script, highlight=False)
