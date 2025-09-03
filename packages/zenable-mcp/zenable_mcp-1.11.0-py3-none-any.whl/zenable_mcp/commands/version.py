import click

from zenable_mcp import __version__
from zenable_mcp.logging.command_logger import log_command
from zenable_mcp.logging.logged_echo import echo


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@log_command
def version():
    """Show the zenable-mcp version"""
    echo(__version__)
