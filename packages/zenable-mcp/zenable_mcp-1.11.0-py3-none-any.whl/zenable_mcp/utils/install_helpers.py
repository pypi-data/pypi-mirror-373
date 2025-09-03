import shutil
from typing import Optional

import click

from zenable_mcp.exceptions import IDECapabilityError
from zenable_mcp.ide_config import (
    create_ide_config,
    get_ide_display_names,
    get_supported_ides,
)
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona
from zenable_mcp.utils.config_manager import backup_config_file
from zenable_mcp.utils.config_validation import check_zenable_config_status
from zenable_mcp.utils.install_status import InstallResult, InstallStatus


def _check_instructions_needed(
    ide_config, existing_config_path: Optional[str], overwrite: bool
) -> bool:
    """Check if instructions file needs to be created or updated.

    Args:
        ide_config: The IDE configuration object
        existing_config_path: Path to existing config file if found
        overwrite: Whether to overwrite existing files

    Returns:
        True if instructions need to be created/updated, False otherwise
    """
    if not ide_config.instructions_file_path:
        return False

    try:
        instructions_path = ide_config.get_instructions_path()
        if not instructions_path.exists():
            echo(
                f"Instructions file missing at {instructions_path}",
                persona=Persona.DEVELOPER,
            )
            return True
        elif overwrite:
            echo(
                f"Will update instructions file at {instructions_path} (--overwrite flag set)",
                persona=Persona.DEVELOPER,
            )
            return True
    except (FileNotFoundError, PermissionError, OSError) as e:
        echo(
            f"Could not check instructions file: {e}",
            persona=Persona.DEVELOPER,
        )
    return False


def _handle_existing_config(
    ide_config,
    existing_config_path: str,
    existing_data: dict,
    api_key: str,
    overwrite: bool,
    dry_run: bool,
    display_name: str,
) -> tuple[Optional[InstallResult], bool]:
    """Handle existing configuration checks and determine if installation should proceed.

    Args:
        ide_config: The IDE configuration object
        existing_config_path: Path to existing config
        existing_data: Existing configuration data
        api_key: API key for configuration
        overwrite: Whether to overwrite existing configuration
        dry_run: Whether this is a dry run
        display_name: Display name of the IDE

    Returns:
        Tuple of (InstallResult if installation should stop, should_overwrite)
    """
    config_status = check_zenable_config_status(
        existing_data, ide_name=ide_config.name, api_key=api_key
    )
    should_overwrite = overwrite

    if config_status.is_configured:
        if config_status.is_compatible:
            # Check if this is a legacy config that needs upgrading
            status = ide_config.check_config_status(existing_data)
            if status == "legacy":
                echo(
                    f"Found previous version configuration for {display_name} in {existing_config_path} - upgrading automatically",
                    persona=Persona.POWER_USER,
                )
                should_overwrite = True  # Force overwrite for legacy
                return None, should_overwrite
            else:
                # Check if we need to create/update instructions file
                needs_instructions = _check_instructions_needed(
                    ide_config, existing_config_path, overwrite
                )

                if not needs_instructions and not overwrite:
                    # Only return early if both no instructions needed AND not overwriting
                    echo(
                        f"Already properly configured for {display_name} in {existing_config_path}",
                        persona=Persona.POWER_USER,
                    )
                    return (
                        InstallResult(
                            status=InstallStatus.ALREADY_INSTALLED,
                            component_name=display_name,
                            message=f"Already configured in {existing_config_path}",
                            details=f"unchanged:{existing_config_path}",  # Add proper details format
                        ),
                        should_overwrite,
                    )

                # Either instructions needed OR overwrite is set, continue with installation
                return None, should_overwrite
        else:
            # Configured but not supported
            echo(
                f"Found unsupported MCP configuration for {display_name} in {existing_config_path}: {config_status.details}",
                persona=Persona.POWER_USER,
            )
            if not overwrite:
                if dry_run:
                    echo(
                        f"  {click.style('⚠', fg='yellow')} Would skip: {existing_config_path} (unsupported configuration)"
                    )
                else:
                    echo(
                        f"  {click.style('⚠', fg='yellow')} Unsupported configuration in {existing_config_path}"
                    )
                    if config_status.details:
                        echo(f"    Details: {config_status.details}")
                    echo("    Use --overwrite to update to supported configuration")
                return InstallResult(
                    status=InstallStatus.ALREADY_INSTALLED_UNSUPPORTED,
                    component_name=display_name,
                    message=f"Unsupported configuration in {existing_config_path}",
                    details=config_status.details
                    if not dry_run
                    else f"unchanged:{existing_config_path}",
                ), should_overwrite
            # Will overwrite unsupported configuration
            if dry_run:
                echo(
                    f"  {click.style('•', fg='cyan')} Would overwrite unsupported configuration: {existing_config_path}"
                )
    return None, should_overwrite


def validate_api_key(api_key: Optional[str], dry_run: bool) -> bool:
    """Validate that an API key is provided when needed.

    Returns:
        True if validation passes, False if API key is missing (in non-dry-run mode).
    """
    if not api_key and not dry_run:
        echo(
            click.style("Error: ", fg="red", bold=True)
            + "No API key provided. Please set ZENABLE_API_KEY environment variable.\n"
            "Visit https://zenable.io/#mcp to get your API key."
        )
        return False
    return True


def determine_ides_to_configure(
    ide: str, is_global: bool = False, force_all: bool = False
) -> list[str]:
    """Determine which IDEs should be configured based on user input."""
    if ide == "all":
        all_ides = get_supported_ides()

        # If force_all is True, return all supported IDEs
        if force_all:
            return all_ides

        # Filter to only installed IDEs
        installed_ides = []
        for ide_name in all_ides:
            try:
                ide_config = create_ide_config(ide_name, is_global=is_global)
                if ide_config.is_installed():
                    installed_ides.append(ide_name)
            except IDECapabilityError:
                # Include IDEs that have capability errors (like windsurf without --global)
                # so they can be handled with proper warnings
                installed_ides.append(ide_name)
            except Exception:
                # If there's any other error checking, skip this IDE
                pass

        ides_to_configure = installed_ides
    else:
        ides_to_configure = [ide]

    return ides_to_configure


def install_ide_configuration(
    ide_name: str,
    api_key: str,
    overwrite: bool,
    dry_run: bool,
    no_instructions: bool,
    is_global: bool = False,
) -> InstallResult:
    """
    Install configuration for a single IDE.
    Returns an InstallResult object with status and details.
    """

    # Get the display name from the IDE registry
    display_names = get_ide_display_names()
    display_name = display_names.get(
        ide_name, ide_name
    )  # Fallback to ide_name if not found

    try:
        # Create IDE config
        ide_config = create_ide_config(ide_name, api_key, is_global)
    except IDECapabilityError as e:
        # Handle IDE capability exceptions (e.g., Windsurf not supporting project-level)
        if dry_run:
            echo(f"  {click.style('⚠', fg='yellow')} Would skip {e.ide_name}: {str(e)}")
        else:
            echo(f"{click.style('Warning:', fg='yellow')} {str(e)}")
        return InstallResult(
            status=InstallStatus.FAILED,
            component_name=display_name,  # Use display_name from registry
            message=str(e),
            details=e.suggestion if hasattr(e, "suggestion") else None,
        )

    try:
        # Use the display name from the config
        display_name = ide_config.display_name

        # Remove individual configuration messages in recursive mode
        # They will be handled by the execute_for_multiple_components function

        # Check existing configuration
        existing_config_path = ide_config.find_config_file()
        expected_config_path = ide_config.get_default_config_path()

        # Normalize paths for comparison
        if existing_config_path:
            existing_config_path = existing_config_path.resolve()
        expected_config_path = expected_config_path.resolve()

        # If we found a config but it's not where we're installing, ignore it
        if existing_config_path and existing_config_path != expected_config_path:
            echo(
                f"Ignoring config at {existing_config_path} (expected location: {expected_config_path})",
                persona=Persona.DEVELOPER,
            )
            existing_config_path = None

        if existing_config_path:
            try:
                existing_data = ide_config.manager.load_json_config(
                    existing_config_path
                )

                # Use helper function to handle existing config
                result, overwrite = _handle_existing_config(
                    ide_config,
                    existing_config_path,
                    existing_data,
                    api_key,
                    overwrite,
                    dry_run,
                    display_name,
                )
                if result:
                    return result

            except (FileNotFoundError, PermissionError, OSError):
                # Error reading config, proceed with installation
                pass

        # Install configuration (or show what would be done)
        if dry_run:
            # Check version compatibility even in dry-run
            ide_config._check_and_warn_version()

            config_path = ide_config.get_default_config_path()
            if not existing_config_path:
                echo(
                    f"No existing MCP configuration found for {display_name}, would create new configuration at: {config_path}",
                    persona=Persona.POWER_USER,
                )
            # Don't print here - just return the result with details
            if existing_config_path:
                # Check if the configuration would actually change
                would_change = ide_config.would_config_change(overwrite=overwrite)

                if not would_change:
                    action = "unchanged"
                elif overwrite:
                    action = "overwrite"
                else:
                    action = "update"
                path = existing_config_path
            else:
                action = "create"
                path = config_path
            return InstallResult(
                status=InstallStatus.SUCCESS,
                component_name=display_name,
                message=f"Would install to {config_path}",
                details=f"{action}:{path}",  # Store action:path for later processing
            )
        else:
            # Check if configuration exists before install
            config_existed_before = existing_config_path is not None

            if not existing_config_path:
                config_path = ide_config.get_default_config_path()
                echo(
                    f"No existing MCP configuration found for {display_name}, creating new configuration at: {config_path}",
                    persona=Persona.POWER_USER,
                )
            else:
                echo(
                    f"Updating existing MCP configuration for {display_name} at: {existing_config_path}",
                    persona=Persona.POWER_USER,
                )

            # Store backup path for potential restoration on failure
            backup_path = None
            legacy_upgrade_attempted = False
            existing_config_path = None

            try:
                # Check if this is a legacy upgrade scenario
                existing_config_path = ide_config.find_config_file()
                if existing_config_path:
                    existing_data = ide_config.manager.load_json_config(
                        existing_config_path
                    )
                    status = ide_config.check_config_status(existing_data)
                    if status == "legacy":
                        legacy_upgrade_attempted = True
                        # Create backup before attempting upgrade
                        backup_path = backup_config_file(existing_config_path)
                        echo(
                            f"Created backup before legacy upgrade: {backup_path}",
                            persona=Persona.DEVELOPER,
                        )

                # Pass dry_run as skip_comment_warning for dry runs
                config_path, install_status = ide_config.install(
                    overwrite=overwrite, skip_comment_warning=dry_run
                )
            except Exception as e:
                # If legacy upgrade failed, restore from backup
                if (
                    legacy_upgrade_attempted
                    and backup_path is not None
                    and backup_path.exists()
                    and existing_config_path is not None
                ):
                    try:
                        shutil.copy2(backup_path, existing_config_path)
                        echo(
                            "Failed to upgrade configuration. Restored original from backup.",
                            persona=Persona.POWER_USER,
                        )
                        echo(
                            f"  {click.style('✗', fg='red')} Legacy upgrade failed: {e}",
                        )
                        return InstallResult(
                            status=InstallStatus.FAILED,
                            component_name=display_name,
                            message="Failed to upgrade configuration (no changes made)",
                            details=str(e),
                        )
                    except Exception as restore_error:
                        echo(
                            f"  {click.style('✗', fg='red')} Failed to restore backup: {restore_error}",
                        )
                        echo(
                            f"    Manual restoration may be needed from: {backup_path}",
                        )
                # Re-raise if not a legacy upgrade scenario or restoration failed
                raise

            # Determine appropriate message based on status
            if install_status == InstallStatus.UPGRADED:
                echo(
                    f"Successfully upgraded {display_name} MCP configuration to the latest format at: {config_path}",
                    persona=Persona.POWER_USER,
                )
                echo(
                    click.style(
                        "✓ Configuration upgraded successfully to latest format",
                        fg="green",
                    )
                )
                message = f"Upgraded to latest format at {config_path}"
            elif install_status == InstallStatus.ALREADY_INSTALLED:
                echo(
                    f"Configuration already up-to-date for {display_name} at: {config_path}",
                    persona=Persona.POWER_USER,
                )
                # Don't return here - continue to collect post-install instructions
                message = f"Already configured in {config_path}"
            elif config_existed_before:
                echo(
                    f"Successfully updated MCP configuration for {display_name} at: {config_path}",
                    persona=Persona.POWER_USER,
                )
                message = f"Updated configuration at {config_path}"
            else:
                echo(
                    f"Successfully installed MCP configuration for {display_name} at: {config_path}",
                    persona=Persona.POWER_USER,
                )
                message = f"Configuration saved to {config_path}"

            if install_status != InstallStatus.ALREADY_INSTALLED:
                echo(
                    f"Configuration saved to: {config_path}", persona=Persona.POWER_USER
                )

            # Collect post-install instructions
            post_install_message = None
            instructions = ide_config.get_post_install_instructions()
            if instructions and not no_instructions:
                post_install_message = f"\n{click.style(f'{display_name.upper()} Setup:', fg='cyan', bold=True)}{instructions}"

            return InstallResult(
                status=install_status,
                component_name=display_name,
                message=message,
                post_install_message=post_install_message,
            )

    except FileNotFoundError as e:
        if dry_run:
            echo(
                f"  {click.style('✗', fg='red')} Would fail: Configuration directory not found: {e}"
            )
        else:
            echo(
                f"  {click.style('✗', fg='red')} Configuration directory not found: {e}"
            )
        return InstallResult(
            status=InstallStatus.FAILED,
            component_name=display_name,
            message="Directory not found",
            details=str(e),
        )
    except PermissionError as e:
        if dry_run:
            echo(f"  {click.style('✗', fg='red')} Would fail: Permission denied: {e}")
        else:
            echo(f"  {click.style('✗', fg='red')} Permission denied: {e}")
        return InstallResult(
            status=InstallStatus.FAILED,
            component_name=display_name,
            message="Permission denied",
            details=str(e),
        )
    except SystemExit:
        # Handle sys.exit() calls from our error handling
        if dry_run:
            echo(f"  {click.style('✗', fg='red')} Would fail during installation")
        else:
            echo(f"  {click.style('✗', fg='red')} Installation failed")
        return InstallResult(
            status=InstallStatus.FAILED,
            component_name=display_name,
            message="Installation failed",
        )
    except Exception as e:
        if dry_run:
            echo(f"  {click.style('✗', fg='red')} Would fail: {e}")
        else:
            echo(f"  {click.style('✗', fg='red')} Failed: {e}")
        return InstallResult(
            status=InstallStatus.FAILED,
            component_name=display_name,
            message="Installation failed",
            details=str(e),
        )
