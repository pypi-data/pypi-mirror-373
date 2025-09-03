import logging

import click

from zenable_mcp.logging.logging_handler import LocalFileHandler


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log messages based on level"""

    def format(self, record):
        # Get the base formatted message
        msg = super().format(record)

        # Add level prefix with distinct styling for debug and verbose
        if record.levelno == logging.DEBUG:
            prefix = click.style("[DEBUG] ", fg="cyan", bold=True)
            styled_msg = click.style(msg, fg="cyan", dim=True)
        elif record.levelno == logging.INFO:
            prefix = click.style("[INFO] ", fg="blue", bold=True)
            styled_msg = click.style(msg, fg="blue")
        elif record.levelno == logging.WARNING:
            prefix = click.style("[WARN] ", fg="yellow", bold=True)
            styled_msg = click.style(msg, fg="yellow")
        elif record.levelno == logging.ERROR:
            prefix = click.style("[ERROR] ", fg="red", bold=True)
            styled_msg = click.style(msg, fg="red")
        else:
            prefix = ""
            styled_msg = msg

        return prefix + styled_msg


def configure_logging(level: int):
    """Configure logging with colored output and comprehensive logging to file

    Args:
        level: The logging level to set
    """
    # Create a colored formatter for console
    console_formatter = ColoredFormatter("%(message)s")

    # Create formatter for file logging
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create and configure a stream handler with colored output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Add local file handler for comprehensive logging
    local_handler = LocalFileHandler()
    local_handler.setLevel(logging.DEBUG)  # Capture all levels in file
    local_handler.setFormatter(file_formatter)
    root_logger.addHandler(local_handler)

    # Suppress noisy third-party loggers
    # FastMCP and its internals - suppress debug messages about SSE/connections
    logging.getLogger("fastmcp").setLevel(logging.WARNING)
    logging.getLogger("fastmcp.client").setLevel(logging.WARNING)
    logging.getLogger("fastmcp.sse").setLevel(logging.WARNING)
    logging.getLogger("fastmcp._client").setLevel(logging.WARNING)

    # HTTP libraries - always suppress verbose connection details
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(
        logging.ERROR
    )  # Very noisy, only show errors

    # Additional HTTP-related loggers that are very noisy
    logging.getLogger("httpcore.http11").setLevel(logging.ERROR)
    logging.getLogger("httpcore.connection").setLevel(logging.ERROR)
    logging.getLogger("httpx._client").setLevel(logging.WARNING)

    # Suppress all httpcore submodules
    logging.getLogger("httpcore._sync").setLevel(logging.ERROR)
    logging.getLogger("httpcore._async").setLevel(logging.ERROR)

    # SSE (Server-Sent Events) related
    logging.getLogger("sse").setLevel(logging.ERROR)
    logging.getLogger("sse_starlette").setLevel(logging.ERROR)
    logging.getLogger("httpx_sse").setLevel(logging.ERROR)

    # GitPython - suppress Popen debug messages
    logging.getLogger("git").setLevel(logging.WARNING)
    logging.getLogger("git.cmd").setLevel(logging.WARNING)
    logging.getLogger("git.util").setLevel(logging.WARNING)

    # Asyncio - suppress selector debug messages
    logging.getLogger("asyncio").setLevel(logging.WARNING)
