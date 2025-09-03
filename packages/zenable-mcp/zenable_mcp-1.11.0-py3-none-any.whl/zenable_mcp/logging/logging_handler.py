import logging
import sys
import traceback
from contextlib import contextmanager

import click

from zenable_mcp.logging.local_logger import get_local_logger


class LocalFileHandler(logging.Handler):
    """Custom logging handler that sends all log records to the local logger."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to the local logger."""
        local_logger = get_local_logger()

        # Format the log message
        msg = self.format(record)

        # Create structured log entry
        log_entry = {
            "type": "log",
            "level": record.levelname,
            "logger": record.name,
            "message": msg,
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
            "pathname": record.pathname,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = traceback.format_exception(*record.exc_info)

        # Log using the local logger
        local_logger.log_command(
            command="python_log",
            args=log_entry,
            result=None,
            error=None,
            duration_ms=None,
        )


@contextmanager
def intercept_click_echo():
    """Context manager for intercepting click.echo calls and logging them.

    Usage:
        with intercept_click_echo():
            # All click.echo calls within this context will be logged
            click.echo("This will be logged")
    """
    original_echo = click.echo

    def wrapped_echo(message=None, file=None, nl=True, err=False, color=None):
        """Wrapper for click.echo that logs the message."""
        try:
            # Call the original echo first
            result = original_echo(message, file, nl, err, color)

            # Log the echo after successful execution
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
                "type": "click_echo",
                "message": str(message) if message is not None else "",
                "stream": output_stream,
                "newline": nl,
                "color": color,
            }

            local_logger.log_command(
                command="click_echo",
                args=log_entry,
                result=None,
                error=None,
                duration_ms=None,
            )

            return result
        except BaseException:
            # Ensure we don't break the original functionality
            raise

    try:
        # Replace click.echo with our wrapper
        click.echo = wrapped_echo
        yield
    finally:
        # Always restore the original function
        click.echo = original_echo


def setup_comprehensive_logging(log_level: int = logging.INFO) -> None:
    """Set up comprehensive logging that captures all log messages.

    Note: For click.echo interception, use the intercept_click_echo context manager.

    Args:
        log_level: The logging level to set
    """
    # Add our custom handler to the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)  # Set the root logger level

    # Check if we already have our handler installed
    has_local_handler = any(
        isinstance(h, LocalFileHandler) for h in root_logger.handlers
    )

    if not has_local_handler:
        # Create and add our local file handler
        local_handler = LocalFileHandler()
        local_handler.setLevel(logging.DEBUG)  # Capture all levels
        local_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        root_logger.addHandler(local_handler)


def teardown_comprehensive_logging() -> None:
    """Remove comprehensive logging setup."""
    # Remove our handler from root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        if isinstance(handler, LocalFileHandler):
            root_logger.removeHandler(handler)
