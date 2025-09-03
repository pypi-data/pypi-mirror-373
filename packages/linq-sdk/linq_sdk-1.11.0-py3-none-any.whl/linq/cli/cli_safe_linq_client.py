from rich.console import Console

from linq.client import Linq

from .cli_safe_wrapper import CliSafeMeta


class CliSafeLinq(Linq, metaclass=CliSafeMeta):
    ...
