import copy
import json
import re
from typing import Any

import typer
from rich.console import Console
from rich.markup import escape
from rich.prompt import Prompt
from rich.tree import Tree

from linq.cli import get_custom_console
from linq.config import Config
from linq.credentials import Credentials
from linq.exceptions import APIError
from linq.parameters import ParameterValue
from linq.schema import workflow_api

ESCAPE_KEY = "q"
ESCAPE_PROMPT = f"Enter '{ESCAPE_KEY}' to abort, or enter a valid value to continue"
TRUE_STRINGS = ("yes", "true", "t", "y", "1")
FALSE_STRINGS = ("no", "false", "f", "n", "0")
VALID_BOOLEAN_STRINGS = TRUE_STRINGS + FALSE_STRINGS


def is_configured() -> None:
    """Callback for typer to guard commands that require a configured SDK."""
    console = get_custom_console()
    config = Config.load()
    if not config.is_configured():
        console.print("CLI is not configured yet - Please run [cyan bold]`linq configure`[/] first.")
        raise typer.Exit(2)


def is_logged_in() -> None:  # pragma: no cover
    """Callback for typer to guard commands that require login."""
    console = get_custom_console()
    credentials = Credentials.load()
    if not credentials.is_configured():
        console.print("CLI is not logged in - Please run [cyan bold]`linq auth login`[/] first.")
        raise typer.Exit(2)
    if credentials.is_expired():
        console.print("CLI login has expired - Please run [cyan bold]`linq auth login`[/] again.")
        raise typer.Exit(2)


def is_configured_and_logged_in() -> None:  # pragma: no cover
    """Callback for typer to guard commands that require a configured SDK and login."""
    is_configured()
    is_logged_in()


def type_raw_bool_param(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if v.lower() not in VALID_BOOLEAN_STRINGS:
        raise ValueError("Not a valid boolean string. Valid values include " + ", ".join(VALID_BOOLEAN_STRINGS))
    return v.lower() in TRUE_STRINGS


def _recursive_parameter_prompt(
    parameter: workflow_api.ParameterDefinition,
    message: str,
) -> ParameterValue:
    """Recursively prompt the user for parameter values."""
    value = Prompt.ask(message)
    if value == ESCAPE_KEY:
        raise KeyboardInterrupt("User aborted parameter input.")
    if value == "" and parameter.default is not None:
        value = parameter.default
    if value == "":
        return _recursive_parameter_prompt(
            parameter, f"No value entered for parameter {parameter.name}. {ESCAPE_PROMPT}"
        )

    try:
        return _validate_parameter_value(parameter, value)
    except ValueError as e:
        return _recursive_parameter_prompt(parameter, f"{e}. {ESCAPE_PROMPT}")


def _validate_parameter_value(parameter: workflow_api.ParameterDefinition, value: Any) -> ParameterValue:
    """Validate a parameter value against the parameter definition."""
    match parameter.type:
        case "boolean":
            try:
                return workflow_api.BooleanParameterValueInput(id=parameter.id, value=type_raw_bool_param(value))
            except ValueError:
                raise ValueError(
                    f"Invalid boolean value for parameter '{parameter.name}'. Valid values include ('"
                    + "', '".join(VALID_BOOLEAN_STRINGS)
                    + "')",
                )
        case "integer":
            try:
                processed_value = int(value)
            except ValueError:
                raise ValueError(f"Invalid integer value for parameter '{parameter.name}'")
            if parameter.minimum is not None and processed_value < parameter.minimum:
                raise ValueError(
                    f"Value for parameter '{parameter.name}' is less than the minimum value of {parameter.minimum}"
                )
            if parameter.maximum is not None and processed_value > parameter.maximum:
                raise ValueError(
                    f"Value for parameter '{parameter.name}' is greater than the maximum value of {parameter.maximum}"
                )
            if parameter.multiple_of is not None and processed_value % parameter.multiple_of != 0:
                raise ValueError(f"Value for parameter '{parameter.name}' is not a multiple of {parameter.multiple_of}")
            return workflow_api.IntegerParameterValueInput(id=parameter.id, value=processed_value)

        case "float":
            try:
                processed_value = float(value)
            except ValueError:
                raise ValueError(f"Invalid float value for parameter '{parameter.name}'")
            if parameter.minimum is not None and processed_value < parameter.minimum:
                raise ValueError(
                    f"Value for parameter '{parameter.name}' is less than the minimum value of {parameter.minimum}"
                )
            if parameter.maximum is not None and processed_value > parameter.maximum:
                raise ValueError(
                    f"Value for parameter '{parameter.name}' is greater than the maximum value of {parameter.maximum}"
                )
            return workflow_api.FloatParameterValueInput(id=parameter.id, value=processed_value)

        case "string":
            if parameter.is_file_path and not _is_valid_file_path(value):
                raise ValueError(f"Invalid file path for parameter '{parameter.name}'")
            if parameter.is_directory_path and not _is_valid_directory(value):
                raise ValueError(f"Invalid directory path for parameter '{parameter.name}'")
            return workflow_api.StringParameterValueInput(id=parameter.id, value=str(value))
    raise ValueError(f"Unsupported parameter type '{parameter.type}'")  # pragma: no cover


def _is_valid_file_path(path: str) -> bool:
    """Validate the format of a file path for both Windows and Linux."""
    windows_path_re = re.compile(r'^(?:[a-zA-Z]:)?\\(?:[^\\\/:*?"<>|\r\n]+\\)*[^\\\/:*?"<>|\r\n]*$')
    linux_path_re = re.compile(r"^(\/?(?:[a-zA-Z0-9._-]+\/)*[a-zA-Z0-9._-]*)$")
    return bool(windows_path_re.match(path) or linux_path_re.match(path))


def _is_valid_directory(path: str) -> bool:
    """Validate the format of a directory path for both Windows and Linux."""
    windows_dir_re = re.compile(r"^[a-zA-Z]:\\(?:[^<>:\"/\\|?*]+\\)*$")
    linux_dir_re = re.compile(r"^(/[^/ ]*)+/?$")

    return bool(windows_dir_re.match(path) or linux_dir_re.match(path))


def get_parameter_values_from_file(
    parameter_definitions: list[workflow_api.ParameterDefinition],
    parameters: str | None,
) -> dict[str, Any]:
    """Load the parameter values from a file if provided."""
    if parameters:
        # load the parameter file
        with open(parameters, "r") as f:
            parameter_values: dict[str, Any] = json.load(f)
        # check for any extra parameters in the file
        extra_parameters = set(parameter_values.keys()) - {param.id for param in parameter_definitions}
        if len(extra_parameters) > 0:
            get_custom_console().print(
                "Warning! The following parameters were not found in the workflow and will be ignored: '"
                + "' ,'".join(extra_parameters)
                + "'.",
                style="yellow",
            )
        return parameter_values
    return {}


def validate_parameter_file(
    parameter_definitions: list[workflow_api.ParameterDefinition], parameter_values: dict[str, Any]
) -> list[ParameterValue]:
    """Get the errors from the parameter file values."""
    errors = []
    processed_parameter_values = []
    for parameter in parameter_definitions:
        provided_value = parameter_values.get(parameter.id)
        if provided_value is None:
            continue  # only concerned with parameters provided in the file
        try:
            processed_parameter_values.append(_validate_parameter_value(parameter, provided_value))
        except ValueError as e:
            errors.append(str(e))
    if len(errors) > 0:
        raise APIError("Encountered the following errors in the parameter file: \n" + "\n".join(errors))
    return processed_parameter_values


def prompt_for_missing_parameter_values(
    definitions_of_missing_values: list[workflow_api.ParameterDefinition],
) -> list[ParameterValue]:
    """Prompt the user for any missing parameter values."""
    user_input_values = []
    for parameter in definitions_of_missing_values:
        base_message = f"Please Enter {parameter.type} value for parameter '{parameter.name}'"
        if parameter.default is not None:
            base_message += f" or hit enter to use default value '{parameter.default}'"
        user_input_values.append(_recursive_parameter_prompt(parameter, base_message))
    return user_input_values


def format_parameter_values(
    parameter_definitions: list[workflow_api.ParameterDefinition],
    parameters: str | None = None,
) -> list[ParameterValue]:
    """
    Optional 'parameters' variable is the path to a file containing the parameter values to use for the workflow.
    This function runs validation on all values in parameter file first, throw an error if any of there are wrong,
    prompting the user with what needs to be fixed. Prompt the user to provide any missing values, and warm them if the
    file contains additional values.
    """
    param_def_copy = copy.copy(parameter_definitions)
    # get the parameter values from the file and validate them
    parameter_values = get_parameter_values_from_file(parameter_definitions, parameters)
    valid_param_values = validate_parameter_file(param_def_copy, parameter_values)

    # prompt the user for any missing values
    definitions_of_missing_values = [param for param in param_def_copy if param.id not in parameter_values]
    valid_param_values.extend(prompt_for_missing_parameter_values(definitions_of_missing_values))

    return valid_param_values


def _get_validation_issue_tree(result: list[workflow_api.WorkflowValidationIssue], color: str) -> Tree:
    """
    Get a rich tree representation of the validation issues.
    """
    tree = Tree("Issues", hide_root=True, guide_style="dim")
    branches = {"": tree}

    for error in sorted(result, key=lambda x: x.loc):
        branch_name = ""
        for loc_index in range(len(error.loc)):
            child_branch_name = ".".join(str(l) for l in error.loc[: loc_index + 1])
            if child_branch_name not in branches:
                if isinstance(error.loc[loc_index], int):
                    # If the next element is an array index, print it as [index]
                    label = f"{[error.loc[loc_index]]}"
                else:
                    label = str(error.loc[loc_index])
                branches[child_branch_name] = branches[branch_name].add(f"[bold]{escape(label)}[/bold]")
            branch_name = child_branch_name
        branches[branch_name].add(f"[{color}]{escape(error.msg)}[/{color}]")

    return tree


def render_workflow_validation_result(result: workflow_api.WorkflowValidationResult, *, console: Console) -> None:
    if result.is_valid:
        console.print("Workflow is valid", style="green")
        return

    if result.errors:
        console.print("Workflow is invalid, see errors below!", style="bold red")
        error_tree = _get_validation_issue_tree(result.errors, "red")
        console.print(error_tree)

    if result.warnings:
        console.print("Warnings", style="bold yellow")
        warning_tree = _get_validation_issue_tree(result.warnings, "yellow")
        console.print(warning_tree)
