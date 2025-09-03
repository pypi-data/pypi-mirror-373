import logging

import click

from zenable_mcp import __version__
from zenable_mcp.commands import check, hook, install, logs, version
from zenable_mcp.logging.command_logger import log_command
from zenable_mcp.logging.local_logger import get_local_logger
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.logging_config import configure_logging
from zenable_mcp.logging.persona import Persona
from zenable_mcp.version_check import check_for_updates


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("--verbose", is_flag=True, help="Enable verbose output")
@click.option("--debug", is_flag=True, help="Enable debug output")
@click.pass_context
@log_command
def cli(ctx, verbose, debug):
    """Zenable - Clean Up Sloppy AI Code and Prevent AI-Created Security Vulnerabilities"""
    # Ensure that ctx.obj exists
    ctx.ensure_object(dict)

    # Configure logging based on flags with colored output
    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    # Configure logging (both console and file)
    configure_logging(log_level)

    # Log where the local logs are being stored
    local_logger = get_local_logger()
    log_path = local_logger.strategy.get_log_file_path()
    echo(f"Local logs are being stored at: {log_path}", persona=Persona.POWER_USER)


# Add commands to the CLI group
cli.add_command(version)
cli.add_command(check)
cli.add_command(hook)
cli.add_command(install)
cli.add_command(logs)


def main():
    """Main entry point"""
    # Check for updates before running the CLI
    check_for_updates(__version__)
    cli()


if __name__ == "__main__":
    main()
