from functools import wraps
from types import FunctionType
from typing import Any, Callable, Type, TypeVar

import typer
from pydantic import ValidationError
from rich.console import Console

from linq.cli.utils import render_workflow_validation_result
from linq.exceptions import APIError
from linq.schema.workflow_api import WorkflowValidationIssue, WorkflowValidationResult

from . import get_custom_console

# Type variable to allow data_locked to work with any function signature
F = TypeVar("F", bound=Callable[..., Any])


def handle_api_error(console: Console) -> Callable[[F], F]:
    """Decorator that wraps a function with handling of APIErrors."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except APIError as e:
                console.print(f"An API Error occurred: {e}", style="red")
                raise typer.Exit(1)
            except ValidationError as e:
                validation_result = WorkflowValidationResult(
                    is_valid=False,
                    errors=[
                        WorkflowValidationIssue(
                            level="error",
                            type=ve.get("type", "Unknown type"),
                            loc=list(ve.get("loc", [])),
                            msg=f'{ve.get("msg", "Unknown error message")}. Input provided: {ve.get("input", "Missing input")}. {ve.get("ctx", "")}',
                        )
                        for ve in e.errors()
                    ],
                    warnings=[],
                )
                render_workflow_validation_result(validation_result, console=console)
                raise typer.Exit(1)

        return wrapper  # type: ignore

    return decorator


class CliSafeMeta(type):
    """Metaclass that automatically applies the handle_api_error decorator to all public methods."""

    def __new__(
        cls: Type["CliSafeMeta"],
        name: str,
        bases: tuple,
        dct: dict[str, Any],
    ) -> "CliSafeMeta":
        console = get_custom_console()
        new = super().__new__(cls, name, bases, dct)

        for base in bases:
            for attr_name in dir(base):
                attr_value = getattr(new, attr_name)
                if (
                    isinstance(attr_value, FunctionType)  # Check if it's a method
                    and not attr_name.startswith("_")  # Check if it's public
                ):
                    setattr(new, attr_name, handle_api_error(console)(attr_value))

        return new
