import importlib.util
import json
import os
import time
from enum import Enum
from pathlib import Path
from threading import Thread
from typing import Annotated, Literal, Optional, cast
from uuid import UUID

import humanize.time
import typer
from rich.columns import Columns
from rich.highlighter import JSONHighlighter
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from linq.cli import get_custom_console
from linq.cli.cli_safe_linq_client import CliSafeLinq
from linq.cli.cli_safe_wrapper import WorkflowValidationResult as WorkflowValidationResultMeta
from linq.client import REASON_NOT_REQUIRED, Linq
from linq.exceptions import APIError, DuplicateWorkflowName
from linq.schema import workflow_api
from linq.visualize import show_instrument_plot, show_labware_plot
from linq.workflow import Workflow

from .utils import format_parameter_values, is_configured_and_logged_in, render_workflow_validation_result

PLAN_RESULT_WATCH_TIMEOUT = 600
PLAN_RESULT_WATCH_INTERVAL = 5

output_HELP = "The return type of command output. `default` prints the default output, `json` prints the raw JSON, `id` prints only the ID."

workflow = typer.Typer(
    name="workflow",
    help="Build and manage workflows.",
    invoke_without_command=True,
    no_args_is_help=True,
    callback=is_configured_and_logged_in,
)

plan = typer.Typer(
    name="plan",
    help="Plan a workflow and get the result.",
    invoke_without_command=True,
    no_args_is_help=True,
    callback=is_configured_and_logged_in,
)
workflow.add_typer(plan, name="plan")


def import_workflow(path: Path, *, object_name: str = "workflow") -> Workflow:
    if not path.is_file():
        raise typer.BadParameter(f"File does not exist: {path.absolute()}")
    if path.suffix != ".py":
        raise typer.BadParameter(f"File should be a python file (.py), got {path.suffix} instead")

    module_name = path.stem

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:  # pragma: no cover
        raise typer.BadParameter(f"Could not load module from path: {path.absolute()}")

    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    if not hasattr(module, object_name):
        raise typer.BadParameter(f"Module '{module_name}' does not have an object named '{object_name}'")

    workflow_obj = getattr(module, object_name)
    if not isinstance(workflow_obj, Workflow):
        raise typer.BadParameter(
            f"'{object_name}' should be an instance of the linq.workflow.Workflow class, got {type(workflow_obj).__name__} instead."
        )

    return workflow_obj


class OutputType(str, Enum):
    DEFAULT = "default"
    JSON = "json"
    ID = "id"


output_values = [output.value for output in OutputType]


@workflow.command()
def create(
    path: Annotated[Path, typer.Argument(help="File path to the python file with the workflow object", exists=True)],
    workflow_object: Annotated[str, typer.Option(help="Name of the workflow object in the file")] = "workflow",
    output: Annotated[OutputType, typer.Option(help=output_HELP)] = OutputType.DEFAULT,
):
    """Create a new [bold]workflow.[/]"""
    workflow = import_workflow(path, object_name=workflow_object)
    console = get_custom_console()
    client = CliSafeLinq()
    info = client.create_workflow(workflow)

    match output:
        case OutputType.ID:
            console.out(info.id)
        case OutputType.JSON:
            console.print_json(info.model_dump_json(indent=2))
        case _:
            console.print(f"Workflow [yellow]{workflow.name}[/] created with ID {info.id}", style="green")


@workflow.command()
def describe(workflow_id: Annotated[UUID, typer.Argument(help="ID of the workflow")]):
    """Retrieve and display the details of a workflow."""
    client = CliSafeLinq()
    workflow_config = client.get_workflow(workflow_id)

    console = get_custom_console()
    console.print(
        Columns(
            [
                Panel(
                    Text(f"{workflow_config.name} {workflow_config.metadata.version}", style="bold"),
                    title="Name",
                    style="blue",
                    title_align="left",
                ),
                Panel(escape(str(workflow_config.metadata.version)), title="Version", title_align="left"),
                Panel(
                    Text("Published " if workflow_config.published else "Not Published"),
                    style="green " if workflow_config.published else "yellow",
                ),
            ],
            expand=True,
        )
    )
    console.print(
        Columns(
            [
                Panel(escape(workflow_config.metadata.description), title="Description", title_align="left"),
                Panel(escape(workflow_config.metadata.author), title="Author", title_align="left"),
            ],
            expand=True,
        )
    )

    # ensure the list of valid values isn't too long to print out
    if len(valid_numbers := workflow_config.metadata.valid_batch_data.valid_batch_numbers) <= 6:
        printable_batch_numbers = str(valid_numbers)
    else:
        first_3 = [str(num) for num in valid_numbers[:3]]
        last_3 = [str(num) for num in valid_numbers[-3:]]
        printable_batch_numbers = f"[{', '.join(first_3)}, ... {', '.join(last_3)}]"
    console.print(
        Columns(
            [
                Panel(
                    escape(printable_batch_numbers),
                    title="Valid Batch Numbers",
                    title_align="left",
                ),
                Panel(
                    escape(workflow_config.metadata.valid_batch_data.reason),
                    title="Reason for Batch Numbers",
                    title_align="left",
                ),
            ]
        )
    )

    tree = Tree("Labware Types", guide_style="dim")
    for labware_type in workflow_config.workflow.labware_types:
        tree.add(Text(f"{labware_type.id}", style="bold"))
    console.print(tree)
    console.line()

    tree = Tree("Labware", guide_style="dim")
    for labware in workflow_config.workflow.labware:
        tree.add(Text(f"{labware.id} {labware.type}", style="bold"))
    console.print(tree)
    console.line()

    tree = Tree("Tasks", guide_style="dim")
    for task_id, task in workflow_config.workflow.tasks.items():
        # TODO: Move this to somewhere sensible
        desc = "" if isinstance(task, workflow_api.Conditional) else task.description
        tree.add(Text(f"{task_id} {desc}", style="bold"))
    console.print(tree)
    console.line()

    tree = Tree("Time Constraints", guide_style="dim")
    for time_constraint in workflow_config.workflow.time_constraints:  # pragma: no cover
        tree.add(Text(f"{time_constraint.id} {time_constraint.type}", style="bold"))
    console.print(tree)


@workflow.command()
# This command is only temporalily made available for all users
def download(
    workflow_id: Annotated[UUID, typer.Argument(help="ID of the workflow")],
    output_path: Annotated[str | None, typer.Option(help=output_HELP)] = None,
    parameters: Annotated[str | None, typer.Option(help="Parameter values to use for simulation")] = None,
):
    """Download a translated workflow JSON."""
    from linq._internal.client import InternalLinq

    client = InternalLinq()
    workflow_config = client.get_workflow(workflow_id)

    if workflow_config.parameter_definitions:
        parameter_values = format_parameter_values(workflow_config.parameter_definitions, parameters)
    else:
        parameter_values = []

    # Cast to input for api translation
    workflow_input = workflow_api.WorkflowConfigInputWithParameters(
        **workflow_config.model_dump(), parameter_values=parameter_values
    )

    workflow_json = client.translate_workflow(workflow_input)
    if output_path:
        if os.path.isdir(output_path):
            output_path = os.path.join(output_path, f"{workflow_config.name}.json")
        with open(output_path, "w") as f:
            json.dump(workflow_json, f, indent=2)
    else:
        console = get_custom_console()
        console.print(workflow_json)


@workflow.command()
def list(
    max_entries: Annotated[int, typer.Option(help="Maximum number of entries to display")] = 30,
    page: Annotated[int, typer.Option(help="What page of entries result to display")] = 1,
):
    """
    Get a list of all workflows.

    :param page: The page number to retrieve.
    :param max_entries: The number of items per page.
    """

    console = get_custom_console()
    client = CliSafeLinq()
    workflows = client.get_workflows(
        page=page,
        page_size=max_entries,
    )
    table = Table(show_header=True, header_style="bold")
    table.add_column("Name", max_width=60)
    table.add_column("ID", min_width=36, no_wrap=True)
    # table.add_column("Version") # TODO: Add proper versioning
    table.add_column("Last Updated")
    table.add_column("Published")

    if not workflows:  # pragma: no cover
        console.print("No workflows found", style="yellow")
        raise typer.Exit(0)

    for workflow in reversed(workflows[:max_entries]):
        table.add_row(
            workflow.name,
            str(workflow.id),
            humanize.time.naturaltime(workflow.updated_at),
            "No" if not workflow.published_at else humanize.time.naturaltime(workflow.published_at),
        )

    console.print(table)


@workflow.command()
def save(
    workflow_id: Annotated[UUID, typer.Argument(help="ID of the workflow to update")],
    path: Annotated[Path, typer.Argument(help="File path to the python file with the workflow object", exists=True)],
    workflow_object: Annotated[str, typer.Option(help="Name of the workflow object in the file")] = "workflow",
    output: Annotated[OutputType, typer.Option(help=output_HELP)] = OutputType.DEFAULT,
):
    """Save a workflow with a given ID. Will update existing workflows or create a new one with the specified ID."""
    workflow = import_workflow(path, object_name=workflow_object)
    console = get_custom_console()
    client = CliSafeLinq()
    updated_workflow = client.update_workflow(workflow_id, workflow)

    match output:
        case OutputType.ID:
            console.out(updated_workflow.id)
        case OutputType.JSON:
            console.print_json(updated_workflow.model_dump_json(indent=2))
        case _:
            console.print(f"Workflow with ID [yellow]{updated_workflow.id}[/] successfully saved", style="green")


@workflow.command()
def delete(
    workflow_id: Annotated[UUID, typer.Argument(help="ID of the workflow to delete")],
    output: Annotated[OutputType, typer.Option(help=output_HELP)] = OutputType.DEFAULT,
):
    """Delete a workflow by ID."""
    console = get_custom_console()
    client = CliSafeLinq()
    client.delete_workflow(workflow_id)

    match output:
        case OutputType.ID:
            console.out(workflow_id)
        case OutputType.JSON:
            console.print_json(json.dumps(dict(workflow_id=str(workflow_id))))
        case _:
            console.print(f"Workflow with ID {workflow_id} deleted", style="green")


@workflow.command()
def validate(
    path: Annotated[Path, typer.Argument(help="File path to the python file with the workflow object", exists=True)],
    workflow_object: Annotated[str, typer.Option(help="Name of the workflow object in the file")] = "workflow",
    validate_drivers: Annotated[
        bool, typer.Option(help="Do additional validation for supported drivers and configuration")
    ] = False,
    validate_infeasibility: Annotated[bool, typer.Option(help="Do additional validation for infeasibility")] = False,
    parameters: Annotated[str | None, typer.Option(help="Parameter values to use for simulation")] = None,
):
    """Validate a workflow."""
    client = CliSafeLinq()
    workflow = import_workflow(path, object_name=workflow_object)

    if validate_drivers:
        # Get all parameter definitions
        required_parameters = workflow.parameter_definitions
    else:
        # Only get the always_required parameters
        required_parameters = [pd for pd in workflow.parameter_definitions if pd.always_required]
    if required_parameters:
        # TODO: Find a better way to do the typing here
        parameter_definitions = [
            cast(workflow_api.ParameterDefinition, pd.to_api_input()) for pd in workflow.parameter_definitions
        ]
        parameter_values = format_parameter_values(parameter_definitions, parameters)
    else:
        parameter_values = []

    result = client.validate_workflow(
        workflow,
        validate_for_execution=validate_drivers,
        validate_for_infeasibility=validate_infeasibility,
        parameter_values=parameter_values,
    )
    render_workflow_validation_result(result, console=get_custom_console())
    if not result.is_valid:
        raise typer.Exit(1)


# TODO [LA-1363]: Allow parameter values in plan start endpoint, for batch parameter values


@plan.command()
def start(
    workflow_id: Annotated[UUID, typer.Argument(help="ID of the workflow to plan")],
    output: Annotated[OutputType, typer.Option(help=output_HELP)] = OutputType.DEFAULT,
    parameters: Annotated[
        str | None,
        typer.Option(
            help="File path to parameter file which contains the static values which will populate the parameter definitions in the config"
        ),
    ] = None,
):
    """Start a plan for a given workflow."""
    console = get_custom_console()
    client = CliSafeLinq()
    parameter_definitions = client.get_workflow_info(workflow_id).parameter_definitions
    required_parameters = [pd for pd in parameter_definitions if pd.always_required]

    result = client.plan_workflow(
        workflow_id=str(workflow_id),
        parameter_values=format_parameter_values(required_parameters, parameters),
    )

    match output:
        case OutputType.ID:
            console.out(result.id)
        case OutputType.JSON:
            console.print_json(result.model_dump_json(indent=2))
        case _:
            console.print(
                f"Plan [yellow]{str(result.status)}[/] with ID {result.id} for workflow with ID {workflow_id}",
                style="green",
            )


@plan.command()
def status(
    workflow_id: Annotated[UUID, typer.Argument(help="ID of the workflow to plan")],
    plan_id: Annotated[UUID, typer.Argument(help="ID of the plan to check")],
):
    """Get the planning status of a workflow."""
    console = get_custom_console()
    client = CliSafeLinq()
    result = client.get_plan_status(str(workflow_id), str(plan_id))

    if result.status == "FAILED":
        console.print(f"{result.error}", style="red")
        raise typer.Exit(1)

    message = f"Workflow planning status: {result.status}"
    if result.stage is not None:
        message += f", stage: {result.stage}"

    console.print(message, style="green")


class VisualizationMode(str, Enum):
    LABWARE = "labware"
    INSTRUMENT = "instrument"
    NONE = "none"


@plan.command()
def result(
    workflow_id: Annotated[UUID, typer.Argument(help="ID of the workflow to plan")],
    plan_id: Annotated[UUID, typer.Argument(help="ID of the plan to check")],
    visualize: Annotated[VisualizationMode, typer.Option(help="Specify what to visualize")] = VisualizationMode.NONE,
    watch: Annotated[int | None, typer.Option(help="Wait for the plan to complete before getting result")] = None,
    silent: Annotated[bool, typer.Option(help="Don't show any output")] = False,
):
    """Get the result of a planned workflow."""
    console = get_custom_console()
    # NOTE: Need to use unsafe client here to enable special behaviour for watch
    client = Linq()

    # If we enable watch, we start a spinner and wait for the plan to complete
    if watch is not None:
        status: Literal["PENDING", "COMPLETED", "FAILED"] = "PENDING"
        watch_time = 0.0

        def run_status():  # pragma: no cover
            with console.status("Waiting for plan to complete...", spinner="bouncingBar"):
                while status == "PENDING" and watch_time < watch:
                    time.sleep(1.0 / 10.0)

        status_thread = Thread(target=run_status)

        status_thread.start()
        try:
            start_time = time.time()
            while watch_time <= watch:
                status_result = client.get_plan_status(str(workflow_id), str(plan_id))
                status = status_result.status
                if status == "COMPLETED":
                    break
                if status == "FAILED":
                    console.print(
                        f"Plan failed with: {status_result.error if status else 'Unknown error!'}\nPlease contact Automata Support for additional help.",
                        style="red",
                    )
                    raise typer.Exit(1)

                time.sleep(PLAN_RESULT_WATCH_INTERVAL)
                watch_time = time.time() - start_time
            else:
                console.print(f"Plan result --watch timed out after {watch}s", style="red")
                raise typer.Exit(1)
        except APIError as e:
            console.print(str(e), style="red")
            status = "FAILED"
            raise typer.Exit(1)

        finally:
            status_thread.join()

    try:
        result = client.get_plan_result(str(workflow_id), str(plan_id))
    except APIError as e:
        console.print(str(e), style="red")
        raise typer.Exit(1)

    match visualize:
        case "instrument":
            show_instrument_plot(result)  # pragma: no cover
        case "labware":
            show_labware_plot(result)  # pragma: no cover
        case _:
            ...
    if not silent:
        highlighter = JSONHighlighter()
        console.print(highlighter(result.model_dump_json(indent=2)))


@workflow.command()
def publish(
    workflow_id: Annotated[UUID, typer.Argument(help="ID of the workflow to publish")],
    plan_id: Annotated[UUID | None, typer.Option(help="The ID of the plan to include when publishing")] = None,
    simulate_time: Annotated[bool, typer.Option(help="Published workflow will run with simulated time")] = False,
    simulate_drivers: Annotated[bool, typer.Option(help="Published workflow will run with simulated drivers.")] = False,
    reason: Annotated[str | None, typer.Option(help="Reason for publishing the workflow")] = None,
    silent: Annotated[bool, typer.Option(help="Don't show any output")] = False,
    output: Annotated[OutputType, typer.Option(help=output_HELP)] = OutputType.DEFAULT,
    overwrite_on_conflict: Annotated[
        bool,
        typer.Option(
            help="Overwrite published workflow with same name without confirmation (WARNING: Permanently deletes existing workflow)"
        ),
    ] = False,
    parameters: Annotated[
        str | None,
        typer.Option(
            help="File path to parameter file which contains the static values which will populate the parameter definitions in the config"
        ),
    ] = None,
):
    """Publish a workflow to make it available for execution on a workcell."""
    console = get_custom_console()
    client = CliSafeLinq()
    workflow_info = client.get_workflow_info(workflow_id)
    parameter_definitions = workflow_info.parameter_definitions

    def do_publish(overwrite: bool):
        return client.publish_workflow(
            workflow_id=workflow_id,
            plan_id_to_include=plan_id,
            simulate_drivers=simulate_drivers,
            simulate_time=simulate_time,
            reason=reason or REASON_NOT_REQUIRED,
            parameter_values=format_parameter_values(parameter_definitions, parameters),
            overwrite_on_conflict=overwrite,
        )

    try:
        published_workflow = do_publish(overwrite_on_conflict)
    except DuplicateWorkflowName:
        if not overwrite_on_conflict:  # pragma: no cover
            console.print(
                f'A workflow with the same name [bold]"{workflow_info.name}"[/bold] already published in the configured environment.'
            )
            console.print(
                "[bold yellow]Warning:[/bold yellow] [yellow]Overwriting it will permanently delete the existing published version.[/yellow]"
            )
            confirm = typer.confirm("Proceed with overwrite?", default=False)
            if not confirm:
                console.print("Publishing aborted", style="yellow")
                raise typer.Exit(1)
        published_workflow = do_publish(True)

    if not silent:
        match output:
            case OutputType.ID:
                console.out(published_workflow.linq_backend_workflow_id)
            case OutputType.JSON:
                console.print_json(published_workflow.model_dump_json(indent=2))
            case _:
                console.print(
                    f"Workflow with ID {published_workflow.workflow_id} published",
                    style="green",
                )


@workflow.command(hidden=True)
def get_puml(
    path: Annotated[Path, typer.Argument(help="File path to the python file with the workflow object", exists=True)],
    workflow_object: Annotated[str, typer.Option(help="Name of the workflow object in the file")] = "workflow",
    # parameters: Annotated[str | None, typer.Option(help="Parameter values to use for simulation")] = None,
):
    """Validate a workflow."""
    console = get_custom_console()
    client = CliSafeLinq()
    workflow = import_workflow(path, object_name=workflow_object)

    result = client.get_workflow_puml(
        workflow,
    )

    before, after = result
    BEFORE_FILE = f"{workflow.name}_before.puml"
    AFTER_FILE = f"{workflow.name}_after.puml"
    with open(BEFORE_FILE, "w") as f:
        f.write(before)
    with open(AFTER_FILE, "w") as f:
        f.write(after)

    console.print(f"PUML files saved as {BEFORE_FILE} and {AFTER_FILE}", style="green")


@plan.command("list")
def list_plans(
    workflow_id: Optional[UUID] = typer.Option(None, help="ID of the workflow to list plans for (optional)"),
):
    """List plans for a workflow or all workflows."""
    console = get_custom_console()
    client = CliSafeLinq()

    table = Table(show_header=True, header_style="bold")
    table.add_column("Name", max_width=60)
    table.add_column("Workflow ID", min_width=36, no_wrap=True)
    table.add_column("Plan ID", min_width=36, no_wrap=True)
    table.add_column("Status", min_width=10)

    workflows = []
    if workflow_id:
        try:
            workflow_info = client.get_workflow_info(workflow_id)
            workflows = [workflow_info]
        except Exception:
            console.print(f"Workflow with ID {workflow_id} not found", style="red")
            return
    else:
        workflows = client.get_workflows()

    found_plans = False
    # good improvement for future is use async client to fetch plans concurrently
    for workflow in workflows:
        try:
            plans = client.list_plans_for_workflow(workflow.id)
        except Exception:
            continue
        for plan in plans or []:
            table.add_row(
                workflow.name,
                str(workflow.id),
                str(plan.id),
                plan.status,
            )
            found_plans = True

    if found_plans:
        console.print(table)
    else:
        msg = f"No plans found for workflow {workflow_id}" if workflow_id else "No plans found for any workflow"
        console.print(msg, style="yellow")
