"""Centralized echo function for all output and logging."""

import logging
import sys

import click

from zenable_mcp.logging.local_logger import get_local_logger
from zenable_mcp.logging.persona import Persona

# Get module logger for internal logging
logger = logging.getLogger(__name__)


def echo(
    message,
    persona=Persona.USER,
    file=None,
    nl=True,
    err=False,
    color=None,
    log=False,
):
    """
    Centralized echo function that handles all output and logging.

    This is the ONLY function that should use click.echo or logging directly.
    All other code should use this function for output.

    Args:
        message: The message to output
        persona: The persona type (USER, POWER_USER, or DEVELOPER)
        file: The file to write to (defaults to stdout/stderr)
        nl: Whether to add a newline
        err: Whether to write to stderr (for warnings/errors)
        color: Color settings for the output
        log: Whether to log the output locally (default: False)
    """
    # Handle output based on persona
    if persona == Persona.DEVELOPER:
        # Developer persona uses debug logging
        logger.debug(message)
    elif persona == Persona.POWER_USER:
        # Power user persona uses info logging
        logger.info(message)
    elif persona == Persona.USER:
        # User persona uses click.echo for visible output
        click.echo(message, file, nl, err, color)
    else:
        # Default to USER behavior if unknown persona
        click.echo(message, file, nl, err, color)

    # Log locally if explicitly requested, or if err=True
    if log or err:
        try:
            local_logger = get_local_logger()

            # Determine the output stream
            output_stream = "stderr" if err else "stdout"
            if file:
                if file == sys.stderr:
                    output_stream = "stderr"
                elif file == sys.stdout:
                    output_stream = "stdout"
                else:
                    output_stream = f"file:{file}"

            log_entry = {
                "type": "echo",
                "message": message,
                "persona": persona.value,
                "stream": output_stream,
                "newline": nl,
                "color": color,
            }

            local_logger.log_command(
                command="echo",
                args=log_entry,
                result=None,
                error=None,
                duration_ms=None,
            )
        except (OSError, IOError) as e:
            print(
                "Error: Encountered a OS/IO Error while attempting to log",
                file=sys.stderr,
            )
            # Attempt to provide more details if running with --verbose or --debug
            logger.info(e)
        except AttributeError as e:
            print(
                "Error: Encountered an AttributeError while attempting to log",
                file=sys.stderr,
            )
            # Attempt to provide more details if running with --verbose or --debug
            logger.info(e)
        except RuntimeError as e:
            print(
                "Error: Encountered a RuntimeError while attempting to log",
                file=sys.stderr,
            )
            # Attempt to provide more details if running with --verbose or --debug
            logger.info(e)
