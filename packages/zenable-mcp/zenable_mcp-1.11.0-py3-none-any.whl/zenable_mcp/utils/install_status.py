"""Shared utilities for handling installation status and results."""

from enum import Enum
from typing import Optional

import click
from pydantic import BaseModel, ConfigDict

from zenable_mcp.exit_codes import ExitCode
from zenable_mcp.logging.logged_echo import echo


class InstallStatus(Enum):
    """Installation status for a component."""

    SUCCESS = "success"  # Successfully installed
    ALREADY_INSTALLED = "already_installed"  # Already properly installed
    ALREADY_INSTALLED_UNSUPPORTED = (
        "already_installed_unsupported"  # Installed but not supported
    )
    UPGRADED = "upgraded"  # Successfully upgraded from legacy format
    FAILED = "failed"  # Installation failed
    SKIPPED = "skipped"  # Skipped (e.g., due to existing config without overwrite)
    CANCELLED = "cancelled"  # User cancelled the operation


class ConfigStatus(BaseModel):
    """Status of Zenable configuration check."""

    model_config = ConfigDict(strict=True)

    is_configured: bool
    is_compatible: bool
    details: Optional[str] = None


class InstallResult:
    """Result of an installation attempt."""

    def __init__(
        self,
        status: InstallStatus,
        component_name: str,
        message: Optional[str] = None,
        details: Optional[str] = None,
        post_install_message: Optional[str] = None,
    ):
        self.status = status
        self.component_name = component_name
        self.message = message
        self.details = details
        self.post_install_message = post_install_message

    @property
    def is_success(self) -> bool:
        """Check if the installation was successful or already properly installed."""
        return self.status in (
            InstallStatus.SUCCESS,
            InstallStatus.ALREADY_INSTALLED,
            InstallStatus.UPGRADED,
        )

    @property
    def is_error(self) -> bool:
        """Check if the installation had an error."""
        return self.status in (
            InstallStatus.FAILED,
            InstallStatus.ALREADY_INSTALLED_UNSUPPORTED,
        )


def categorize_results(results: list[InstallResult]) -> dict[str, list[InstallResult]]:
    """Categorize installation results by status.

    Returns:
        Dictionary with keys: 'success', 'already_installed',
        'already_installed_unsupported', 'upgraded', 'failed', 'skipped', 'cancelled'
    """
    categorized = {
        "success": [],
        "already_installed": [],
        "already_installed_unsupported": [],
        "upgraded": [],
        "failed": [],
        "skipped": [],
        "cancelled": [],
    }

    for result in results:
        if result.status == InstallStatus.SUCCESS:
            categorized["success"].append(result)
        elif result.status == InstallStatus.ALREADY_INSTALLED:
            categorized["already_installed"].append(result)
        elif result.status == InstallStatus.ALREADY_INSTALLED_UNSUPPORTED:
            categorized["already_installed_unsupported"].append(result)
        elif result.status == InstallStatus.UPGRADED:
            categorized["upgraded"].append(result)
        elif result.status == InstallStatus.FAILED:
            categorized["failed"].append(result)
        elif result.status == InstallStatus.SKIPPED:
            categorized["skipped"].append(result)
        elif result.status == InstallStatus.CANCELLED:
            categorized["cancelled"].append(result)

    return categorized


def show_installation_summary(
    results: list[InstallResult],
    dry_run: bool = False,
    install_type: str = "Installation",
) -> None:
    """Display the installation summary with proper categorization.

    Args:
        results: List of installation results
        dry_run: Whether this is a dry-run
        install_type: Type of installation (e.g., "MCP Installation", "Hooks Installation")
    """
    categorized = categorize_results(results)

    echo("\n" + "=" * 60)
    if dry_run:
        echo(
            click.style(f"{install_type} Preview (Dry-Run Mode)", fg="white", bold=True)
        )
    else:
        echo(click.style(f"{install_type} Summary", fg="white", bold=True))
    echo("=" * 60)

    # Show successfully installed
    if categorized["success"]:
        components = [r.component_name for r in categorized["success"]]
        if dry_run:
            echo(
                f"\n{click.style('• Would install:', fg='cyan', bold=True)} {', '.join(components)}"
            )
        else:
            echo(
                f"\n{click.style('✓ Successfully installed:', fg='green', bold=True)} {', '.join(components)}"
            )

    # Show already installed (properly)
    if categorized["already_installed"]:
        components = [r.component_name for r in categorized["already_installed"]]
        if dry_run:
            echo(
                f"\n{click.style('• Already installed:', fg='green', bold=True)} {', '.join(components)}"
            )
        else:
            echo(
                f"\n{click.style('✓ Already installed:', fg='green', bold=True)} {', '.join(components)}"
            )

    # Show upgraded installations
    if categorized["upgraded"]:
        components = [r.component_name for r in categorized["upgraded"]]
        if dry_run:
            echo(
                f"\n{click.style('• Would upgrade:', fg='cyan', bold=True)} {', '.join(components)}"
            )
        else:
            echo(
                f"\n{click.style('✓ Successfully upgraded:', fg='green', bold=True)} {', '.join(components)}"
            )

    # Show already installed but unsupported
    if categorized["already_installed_unsupported"]:
        echo(
            f"\n{click.style('⚠ Already installed (unsupported configuration):', fg='yellow', bold=True)}"
        )
        for result in categorized["already_installed_unsupported"]:
            msg = f"  - {result.component_name}"
            if result.details:
                msg += f": {result.details}"
            echo(msg)

    # Show failed installations
    if categorized["failed"]:
        components = [r.component_name for r in categorized["failed"]]
        if dry_run:
            echo(
                f"\n{click.style('• Would fail:', fg='red', bold=True)} {', '.join(components)}"
            )
        else:
            echo(
                f"\n{click.style('✗ Failed:', fg='red', bold=True)} {', '.join(components)}"
            )

    # Show skipped installations
    if categorized["skipped"]:
        components = [r.component_name for r in categorized["skipped"]]
        echo(
            f"\n{click.style('• Skipped:', fg='yellow', bold=True)} {', '.join(components)}"
        )

    # Show cancelled installations
    if categorized["cancelled"]:
        components = [r.component_name for r in categorized["cancelled"]]
        echo(
            f"\n{click.style('• Cancelled:', fg='yellow', bold=True)} {', '.join(components)}"
        )


def get_exit_code(results: list[InstallResult]) -> int:
    """Determine the appropriate exit code based on installation results.

    Returns:
        SUCCESS if all succeeded or were already properly installed
        INSTALLATION_ERROR if any had unsupported configurations or failures
        PARTIAL_SUCCESS if mixed success/failure (partial success)
    """
    categorized = categorize_results(results)

    has_success = bool(
        categorized["success"]
        or categorized["already_installed"]
        or categorized["upgraded"]
    )
    has_unsupported = bool(categorized["already_installed_unsupported"])
    has_failures = bool(categorized["failed"])
    has_cancelled = bool(categorized["cancelled"])

    if has_unsupported or (has_failures and not has_success):
        return ExitCode.INSTALLATION_ERROR  # Error condition
    elif has_cancelled and not has_success:
        return ExitCode.INSTALLATION_ERROR  # Cancelled with no successes
    elif (has_failures or has_cancelled) and has_success:
        return ExitCode.PARTIAL_SUCCESS  # Partial success
    else:
        return ExitCode.SUCCESS  # Full success (including already installed)


def show_post_install_instructions(
    results: list[InstallResult], no_instructions: bool = False, dry_run: bool = False
) -> None:
    """Display post-installation instructions from results."""
    if no_instructions or dry_run:
        return

    post_install_messages = [
        r.post_install_message
        for r in results
        if r.post_install_message and r.status == InstallStatus.SUCCESS
    ]

    if post_install_messages:
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
