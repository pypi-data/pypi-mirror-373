"""CLI validation utilities for zenable_mcp commands."""

import sys
from typing import Union

import click

from zenable_mcp.exit_codes import ExitCode
from zenable_mcp.logging.logged_echo import echo


def validate_mutual_exclusivity(
    first: bool,
    second: bool,
    first_name: str = "first option",
    second_name: str = "second option",
) -> None:
    """Validate that two boolean options are mutually exclusive.

    Args:
        first: Whether the first option is set
        second: Whether the second option is set
        first_name: Display name for the first option (default: "first option")
        second_name: Display name for the second option (default: "second option")

    Exits:
        With ExitCode.INVALID_PARAMETERS if both options are set
    """
    if first and second:
        echo(f"{first_name} and {second_name} are mutually exclusive", err=True)
        sys.exit(ExitCode.INVALID_PARAMETERS)


def handle_exit_code(
    ctx: click.Context, exit_code: Union[int, ExitCode]
) -> Union[int, ExitCode]:
    """Handle exit codes consistently across commands.

    If the command was invoked from a parent command (ctx.parent.parent exists),
    return the exit code so the parent can aggregate results.
    Otherwise, exit the process with the given code.

    Args:
        ctx: Click context
        exit_code: The exit code to handle

    Returns:
        The exit code if invoked from parent, otherwise exits the process
    """
    if ctx.parent and ctx.parent.parent:
        return exit_code
    else:
        ctx.exit(int(exit_code))
