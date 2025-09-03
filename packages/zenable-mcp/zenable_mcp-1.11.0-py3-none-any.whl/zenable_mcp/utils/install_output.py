import click

from zenable_mcp.exit_codes import ExitCode
from zenable_mcp.logging.logged_echo import echo


def show_installation_summary(
    successful_installs: list[str], failed_installs: list[str], dry_run: bool
) -> None:
    """Display the installation summary."""
    echo("\n" + "=" * 60)
    if dry_run:
        echo(click.style("Installation Preview (No-Op Mode)", fg="white", bold=True))
    else:
        echo(click.style("Installation Summary", fg="white", bold=True))
    echo("=" * 60)

    if successful_installs:
        if dry_run:
            echo(
                f"\n{click.style('• Would install:', fg='cyan', bold=True)} {', '.join(successful_installs)}"
            )
        else:
            echo(
                f"\n{click.style('✓ Successful:', fg='green', bold=True)} {', '.join(successful_installs)}"
            )

    if failed_installs:
        if dry_run:
            echo(
                f"\n{click.style('• Would skip/fail:', fg='yellow', bold=True)} {', '.join(failed_installs)}"
            )
        else:
            echo(
                f"\n{click.style('✗ Failed:', fg='red', bold=True)} {', '.join(failed_installs)}"
            )


def show_post_install_instructions(
    post_install_messages: list[str], no_instructions: bool, dry_run: bool
) -> None:
    """Display post-installation instructions."""
    if post_install_messages and not no_instructions and not dry_run:
        echo("\n" + "=" * 60)
        echo(click.style("Post-Installation Instructions", fg="white", bold=True))
        echo("=" * 60)
        for message in post_install_messages:
            echo(message)

        echo("\n" + "=" * 60)
        echo(click.style("Next Steps", fg="white", bold=True))
        echo("=" * 60)
        echo("\n1. Complete the setup instructions above for each IDE")
        echo("2. Restart your IDE(s) to load the new configuration")
        echo(
            "3. Visit https://docs.zenable.io/integrations/mcp/troubleshooting for help"
        )


def show_dry_run_preview(successful_installs: list[str], dry_run: bool) -> None:
    """Display what would happen in dry-run mode."""
    if dry_run and successful_installs:
        echo(
            "\nTo actually perform the installation, run the command without --dry-run"
        )


def get_exit_code(successful_installs: list[str], failed_installs: list[str]) -> int:
    """Determine the appropriate exit code based on installation results."""
    if failed_installs and not successful_installs:
        return ExitCode.INSTALLATION_ERROR  # Complete failure
    elif failed_installs:
        return ExitCode.PARTIAL_SUCCESS  # Partial success
    else:
        return ExitCode.SUCCESS  # Full success


def dry_run_log(message: str, indent: int = 0) -> None:
    """Log a message in dry-run mode with consistent formatting.

    Args:
        message: The message to log
        indent: Number of spaces to indent (0, 2, 4, or 6)
    """
    prefix = " " * indent
    echo(f"{prefix}{message}")
