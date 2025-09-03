import functools
import time
from typing import Any, Callable

import click

from zenable_mcp.logging.local_logger import log_command_execution


def log_command(func: Callable) -> Callable:
    """Decorator to automatically log command execution."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Extract the command name
        command_name = func.__name__

        # Get the click context if available
        ctx = None
        for arg in args:
            if isinstance(arg, click.Context):
                ctx = arg
                break

        # Build args dictionary for logging
        log_args = {}

        # Add all kwargs (these are the click options/arguments)
        log_args.update(kwargs)

        # If we have a context, add parent command info
        if ctx:
            if ctx.parent:
                parent_command = ctx.parent.info_name
                if parent_command:
                    command_name = f"{parent_command}.{command_name}"

            # Add context params if they exist
            if hasattr(ctx, "params"):
                log_args.update(ctx.params)

        # Start timer
        start_time = time.time()

        # Execute the command
        error = None
        result = None
        result_data = None  # Initialize result_data to avoid UnboundLocalError
        try:
            result = func(*args, **kwargs)

            # Try to extract meaningful result data
            if result is not None:
                if isinstance(result, (str, int, float, bool, list, dict)):
                    result_data = {"return_value": result}
                else:
                    result_data = {"return_type": type(result).__name__}
            else:
                result_data = None

            return result

        except Exception as e:
            error = str(e)
            raise

        finally:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log the command execution
            log_command_execution(
                command=command_name,
                args=log_args,
                result=result_data,
                error=error,
                duration_ms=duration_ms,
            )

    return wrapper
