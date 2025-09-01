import logging
from typing import Callable, ParamSpec, TypeVar

import click
from llama_deploy.cli.interactive_prompts.session_utils import is_interactive_session

from .debug import setup_file_logging

P = ParamSpec("P")
R = TypeVar("R")


def global_options(f: Callable[P, R]) -> Callable[P, R]:
    """Common decorator to add global options to command groups"""

    def debug_callback(ctx: click.Context, param: click.Parameter, value: str) -> str:
        if value:
            setup_file_logging(level=logging._nameToLevel.get(value, logging.INFO))
        return value

    return click.option(
        "--log-level",
        type=click.Choice(
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
        ),
        help="Enable debug logging to file",
        callback=debug_callback,
        expose_value=False,
        is_eager=True,
        hidden=True,
    )(f)


def interactive_option(f: Callable[P, R]) -> Callable[P, R]:
    """Add an interactive option to the command"""

    default = is_interactive_session()
    return click.option(
        "--interactive/--no-interactive",
        help="Run in interactive mode. If not provided, will default to the current session's interactive state.",
        is_flag=True,
        default=default,
    )(f)
