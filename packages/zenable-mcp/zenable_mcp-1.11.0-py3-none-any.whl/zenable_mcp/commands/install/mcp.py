import logging
import sys
from pathlib import Path
from typing import Optional, Union

import click

from zenable_mcp.exit_codes import ExitCode
from zenable_mcp.ide_config import create_ide_config
from zenable_mcp.logging.command_logger import log_command
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.utils.cli_validators import (
    handle_exit_code,
    validate_mutual_exclusivity,
)
from zenable_mcp.utils.context_helpers import (
    get_api_key_from_context,
    get_dry_run_from_context,
    get_git_repos_from_context,
    get_is_global_from_context,
    get_recursive_from_context,
)
from zenable_mcp.utils.install_helpers import (
    determine_ides_to_configure,
    install_ide_configuration,
    validate_api_key,
)
from zenable_mcp.utils.install_report import (
    filter_git_repositories,
    show_complete_filtering_information,
    show_filtering_results,
)
from zenable_mcp.utils.install_status import (
    InstallResult,
    InstallStatus,
    get_exit_code,
    show_installation_summary,
    show_post_install_instructions,
)
from zenable_mcp.utils.recursive_operations import (
    _display_overall_summary,
    execute_for_multiple_components,
    find_git_repositories,
)

log = logging.getLogger(__name__)


def _install_mcp_recursive(
    ctx,
    ides: list[str],
    overwrite: bool,
    no_instructions: bool,
    dry_run: bool,
    include_patterns: Optional[list[str]] = None,
    exclude_patterns: Optional[list[str]] = None,
    silent: bool = False,
    return_results: bool = False,
) -> Union[list, ExitCode]:
    """Install MCP for specified IDEs in all git repositories below current directory.

    Args:
        ctx: Click context
        ides: List of IDE names to configure
        overwrite: Whether to overwrite existing configuration
        no_instructions: Whether to suppress post-install instructions
        dry_run: Whether this is a dry run
        include_patterns: Optional list of glob patterns to include directories
        exclude_patterns: Optional list of glob patterns to exclude directories
        silent: Whether to suppress output
        return_results: Whether to return results instead of exit code
    """
    # Get repos from context using helper
    git_repos = get_git_repos_from_context(ctx)
    if git_repos is None:
        git_repos = find_git_repositories()
        # Store for other commands to use
        if ctx.obj:
            ctx.obj["git_repos"] = git_repos

    # Apply filtering if patterns are provided
    original_count = len(git_repos)
    filter_result = filter_git_repositories(
        git_repos,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        handler_name="recursive install",
    )
    git_repos = filter_result.filtered_repos

    if not silent:
        # Check if all repositories were filtered out
        if (include_patterns or exclude_patterns) and len(git_repos) == 0:
            show_filtering_results(
                filter_result.original_count,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
            )
            if return_results:
                return []
            return ExitCode.SUCCESS

        # Show complete filtering information
        if not show_complete_filtering_information(
            git_repos,
            original_count,
            include_patterns or exclude_patterns,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            dry_run=dry_run,
            ask_confirmation=True,
        ):
            if return_results:
                return []
            return ExitCode.SUCCESS

    if not git_repos:
        if not silent and not (include_patterns or exclude_patterns):
            # Only show message if not filtered (filtering messages shown above)
            echo("No git repositories found in the current directory or below.")
        if return_results:
            return []
        return ExitCode.SUCCESS  # No files is not an error

    if not silent:
        if dry_run:
            echo(
                "\n"
                + click.style("DRY RUN MODE:", fg="yellow", bold=True)
                + " Showing what would be done\n"
            )

    # Define the operation function for each repository/IDE combination
    def install_operation(
        repo_path: Path, ide_name: str, dry_run: bool
    ) -> InstallResult:
        # Get API key from context using helper
        api_key = get_api_key_from_context(ctx)
        if not validate_api_key(api_key, dry_run):
            return InstallResult(
                status=InstallStatus.FAILED,
                component_name=ide_name,
                message="Missing API key",
            )

        return install_ide_configuration(
            ide_name,
            api_key,
            overwrite,
            dry_run,
            no_instructions,
            is_global=False,
        )

    # Execute the operation across all repos and IDEs
    all_results = execute_for_multiple_components(
        paths=git_repos,
        components=ides,
        operation_func=install_operation,
        dry_run=dry_run,
        component_type="IDEs",
        silent=silent,
    )

    if not silent:
        # Display overall summary (the utility already shows per-repo results)
        _display_overall_summary(all_results, dry_run)

    # If asked to return results (for parent aggregation), return them
    if return_results:
        return all_results

    # Return appropriate exit code
    failed_count = sum(1 for _, r in all_results if r.is_error)
    if failed_count > 0:
        return ExitCode.INSTALLATION_ERROR
    else:
        return ExitCode.SUCCESS


def _install_mcp_for_ides(
    ctx,
    ides: list[str],
    overwrite: bool,
    no_instructions: bool,
    dry_run: bool,
    is_global: bool,
    force_all: bool = False,
) -> ExitCode:
    """Common function to install MCP for specified IDEs."""
    # Get API key from context using helper
    api_key = get_api_key_from_context(ctx)

    # Validate API key - returns False if missing in non-dry-run mode
    if not validate_api_key(api_key, dry_run):
        return ExitCode.MISSING_API_KEY

    if not dry_run and len(ides) > 1:
        # Get display names for the IDEs that support the requested mode
        ide_display_names = []
        for ide in ides:
            try:
                config = create_ide_config(ide, is_global=is_global)
                # Only include IDEs that support the requested installation mode
                if (is_global and config.supports_mcp_global_config) or (
                    not is_global and config.supports_mcp_project_config
                ):
                    ide_display_names.append(config.name)
            except (ValueError, KeyError, Exception):
                # If we can't determine support, include it and let later validation handle it
                echo(
                    f"Failed to get display name for IDE {ide}; falling back to {ide}...",
                    err=True,
                )
                ide_display_names.append(ide)

        if ide_display_names:
            ides_list = ", ".join(ide_display_names)
            if force_all:
                echo(f"Installing the MCP server for ALL supported IDEs: {ides_list}")
            else:
                echo(
                    f"Installing the MCP server for the following auto-detected IDEs: {ides_list}"
                )

    # Track results
    results: list[InstallResult] = []

    # Install for each IDE
    for ide_name in ides:
        result = install_ide_configuration(
            ide_name, api_key, overwrite, dry_run, no_instructions, is_global
        )
        results.append(result)

    # In dry-run mode, display grouped file operations
    if dry_run:
        files_to_create = []
        files_to_modify = []
        files_to_overwrite = []
        files_unchanged = []

        for result in results:
            if result.details and ":" in result.details:
                parts = result.details.split(":", 1)
                if len(parts) == 2:
                    action, path = parts
                    if action == "create":
                        files_to_create.append(path)
                    elif action == "update":
                        files_to_modify.append(path)
                    elif action == "overwrite":
                        files_to_overwrite.append(path)
                    elif action == "unchanged":
                        files_unchanged.append(path)

        # Display grouped operations
        if files_to_create:
            echo(f"\n{click.style('Would create:', fg='cyan', bold=True)}")
            for path in files_to_create:
                echo(f"  • {path}")

        if files_to_modify:
            echo(f"\n{click.style('Would modify:', fg='cyan', bold=True)}")
            for path in files_to_modify:
                echo(f"  • {path}")

        if files_to_overwrite:
            echo(f"\n{click.style('Would overwrite:', fg='cyan', bold=True)}")
            for path in files_to_overwrite:
                echo(f"  • {path}")

        if files_unchanged:
            echo(f"\n{click.style('Already up-to-date:', fg='green', bold=True)}")
            for path in files_unchanged:
                echo(f"  • {path}")

    # Show summary
    show_installation_summary(results, dry_run, "MCP Installation")

    # Show post-install instructions
    show_post_install_instructions(results, no_instructions, dry_run)

    # In dry-run mode, show preview message
    if dry_run and any(r.is_success for r in results):
        echo(
            "\nTo actually perform the installation, run the command without --dry-run"
        )

    # Get the exit code
    return get_exit_code(results)


# Create options that will be shared by all subcommands
def common_options(f):
    """Decorator to add common options to all MCP subcommands."""
    f = click.option(
        "--overwrite",
        is_flag=True,
        default=False,
        help="Overwrite existing Zenable configuration if it exists",
    )(f)
    f = click.option(
        "--no-instructions",
        is_flag=True,
        default=False,
        help="Don't show post-installation instructions",
    )(f)
    f = click.option(
        "--dry-run",
        is_flag=True,
        default=False,
        help="Show what would be done without actually performing the installation",
    )(f)
    f = click.option(
        "--global",
        "-g",
        "is_global",
        is_flag=True,
        default=False,
        help="Install globally in user's home directory instead of project directory",
    )(f)
    f = click.option(
        "--recursive",
        is_flag=True,
        default=False,
        help="Install in all git repositories found below the current directory",
    )(f)
    f = click.option(
        "--include",
        multiple=True,
        help="Include only directories matching these glob patterns (e.g., '**/microservice-*')",
    )(f)
    f = click.option(
        "--exclude",
        multiple=True,
        help="Exclude directories matching these glob patterns",
    )(f)
    f = click.option(
        "--all",
        "force_all",
        is_flag=True,
        default=False,
        help="Install for all supported IDEs, even if not currently installed",
    )(f)
    return f


@click.group(
    invoke_without_command=True,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be done without actually performing the installation",
)
@click.option(
    "--recursive",
    is_flag=True,
    default=False,
    help="Install in all git repositories found below the current directory",
)
@click.option(
    "--global",
    "-g",
    "is_global",
    is_flag=True,
    default=False,
    help="Install globally in user's home directory instead of project directory",
)
@click.option(
    "--include",
    multiple=True,
    help="Include only directories matching these glob patterns (e.g., '**/microservice-*')",
)
@click.option(
    "--exclude",
    multiple=True,
    help="Exclude directories matching these glob patterns",
)
@click.option(
    "--all",
    "force_all",
    is_flag=True,
    default=False,
    help="Install for all supported IDEs, even if not currently installed",
)
@click.pass_context
@log_command
def mcp(ctx, dry_run, recursive, is_global, include, exclude, force_all):
    """Install Zenable MCP server configuration.

    **Requires ZENABLE_API_KEY environment variable to be set.**

    \b
    Examples:
      # Install MCP for all supported IDEs (default)
      zenable-mcp install mcp
      zenable-mcp install mcp all
    \b
      # Install MCP globally for all supported IDEs
      zenable-mcp install mcp --global
      zenable-mcp install mcp all --global
    \b
      # Install MCP for a specific IDE
      zenable-mcp install mcp cursor
      zenable-mcp install mcp claude
    \b
      # Preview what would be done without installing
      zenable-mcp install mcp --dry-run
      zenable-mcp install mcp cursor --dry-run

    \b
    For more information, visit:
    https://docs.zenable.io/integrations/mcp
    """
    # Check for mutual exclusivity of --global and --recursive
    validate_mutual_exclusivity(is_global, recursive, "--global", "--recursive")

    # Validate that --include and --exclude require --recursive
    if (include or exclude) and not recursive:
        echo(
            click.style("Error: ", fg="red", bold=True)
            + "--include and --exclude options require --recursive to be set",
            err=True,
        )
        sys.exit(ExitCode.INVALID_PARAMETERS)

    # Store dry_run, is_global, recursive, and patterns in context for subcommands
    ctx.ensure_object(dict)

    # Inherit from parent context if not explicitly set
    if not dry_run and ctx.parent and ctx.parent.obj:
        dry_run = ctx.parent.obj.get("dry_run", False)
    if not is_global:
        is_global = get_is_global_from_context(ctx)

    ctx.obj["dry_run"] = dry_run
    ctx.obj["is_global"] = is_global
    ctx.obj["recursive"] = recursive
    ctx.obj["include_patterns"] = list(include) if include else None
    ctx.obj["exclude_patterns"] = list(exclude) if exclude else None
    ctx.obj["force_all"] = force_all

    # Pass through git_repos from parent context if available
    if ctx.parent and ctx.parent.obj and "git_repos" in ctx.parent.obj:
        ctx.obj["git_repos"] = ctx.parent.obj["git_repos"]

    # If no subcommand is provided, default to 'all'
    if ctx.invoked_subcommand is None:
        # Get parent's recursive flag if available
        if not recursive and ctx.parent and ctx.parent.obj:
            recursive = ctx.parent.obj.get("recursive", False)

        ctx.invoke(
            all_ides,
            overwrite=False,
            no_instructions=False,
            dry_run=dry_run,
            is_global=is_global,
            recursive=recursive,
            include=include,
            exclude=exclude,
            force_all=force_all,
        )


@mcp.command(name="all")
@common_options
@click.pass_context
@log_command
def all_ides(
    ctx,
    overwrite,
    no_instructions,
    dry_run,
    is_global,
    recursive,
    include,
    exclude,
    force_all,
):
    """Install MCP for all supported IDEs."""
    # Check for mutual exclusivity of --global and --recursive
    validate_mutual_exclusivity(is_global, recursive, "--global", "--recursive")

    # Get flags from context hierarchy if not explicitly set
    if not dry_run:
        dry_run = get_dry_run_from_context(ctx)
    if not is_global:
        is_global = get_is_global_from_context(ctx)
    if not recursive:
        recursive = get_recursive_from_context(ctx)

    # Check if we're being called from parent install command
    from_parent_install = ctx.obj and ctx.obj.get("from_parent_install", False)

    # Get force_all from context if not explicitly set
    if not force_all and ctx.obj:
        force_all = ctx.obj.get("force_all", False)

    ides = determine_ides_to_configure("all", is_global, force_all=force_all)

    if recursive:
        # Get patterns from context if not explicitly provided
        include_patterns = (
            list(include) if include else (ctx.obj.get("include_patterns") or [])
        )
        exclude_patterns = (
            list(exclude) if exclude else (ctx.obj.get("exclude_patterns") or [])
        )

        result = _install_mcp_recursive(
            ctx,
            ides,
            overwrite,
            no_instructions,
            dry_run,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            silent=from_parent_install,
            return_results=from_parent_install,
        )
        # If called from parent, return results for aggregation
        if from_parent_install:
            return result
        exit_code = result
    else:
        exit_code = _install_mcp_for_ides(
            ctx,
            ides,
            overwrite,
            no_instructions,
            dry_run,
            is_global,
            force_all=force_all,
        )

    return handle_exit_code(ctx, exit_code)


def _install_single_ide(
    ctx,
    ide_name: str,
    overwrite: bool,
    no_instructions: bool,
    dry_run: bool,
    is_global: bool,
    recursive: bool,
    include: tuple,
    exclude: tuple,
    custom_message: str = None,
) -> ExitCode:
    """Helper function to install MCP for a single IDE, reducing code duplication."""
    # Check for mutual exclusivity of --global and --recursive
    validate_mutual_exclusivity(is_global, recursive, "--global", "--recursive")

    # Validate that --include and --exclude require --recursive
    if (include or exclude) and not recursive:
        echo(
            click.style("Error: ", fg="red", bold=True)
            + "--include and --exclude options require --recursive to be set",
            err=True,
        )
        sys.exit(ExitCode.INVALID_PARAMETERS)

    # Get flags from context hierarchy if not explicitly set
    if not is_global:
        is_global = get_is_global_from_context(ctx)
    if not dry_run:
        dry_run = get_dry_run_from_context(ctx)
    if not recursive:
        recursive = get_recursive_from_context(ctx)

    # Display custom message or default message
    if not dry_run and not recursive:
        if custom_message:
            echo(custom_message)
        else:
            # Get display name for the IDE
            try:
                config = create_ide_config(ide_name, is_global=is_global)
                display_name = config.name
            except (ValueError, KeyError):
                echo(
                    f"Warning: Failed to get display name for IDE {ide_name}", err=True
                )
                display_name = ide_name.title()
            except Exception:
                # Don't fail here, let the actual installation handle the error
                display_name = ide_name.title()

            location = "globally" if is_global else "locally"
            echo(
                f"Installing Zenable MCP configuration for {display_name} {location}..."
            )

    if recursive:
        # Get patterns from context if not explicitly provided
        include_patterns = (
            list(include) if include else (ctx.obj.get("include_patterns") or [])
        )
        exclude_patterns = (
            list(exclude) if exclude else (ctx.obj.get("exclude_patterns") or [])
        )

        exit_code = _install_mcp_recursive(
            ctx,
            [ide_name],
            overwrite,
            no_instructions,
            dry_run,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
        )
    else:
        exit_code = _install_mcp_for_ides(
            ctx, [ide_name], overwrite, no_instructions, dry_run, is_global
        )

    return handle_exit_code(ctx, exit_code)


@mcp.command()
@common_options
@click.pass_context
@log_command
def cursor(
    ctx,
    overwrite,
    no_instructions,
    dry_run,
    is_global,
    recursive,
    include,
    exclude,
    force_all,
):
    """Install MCP for Cursor IDE."""
    return _install_single_ide(
        ctx,
        "cursor",
        overwrite,
        no_instructions,
        dry_run,
        is_global,
        recursive,
        include,
        exclude,
    )


@mcp.command()
@common_options
@click.pass_context
@log_command
def windsurf(
    ctx,
    overwrite,
    no_instructions,
    dry_run,
    is_global,
    recursive,
    include,
    exclude,
    force_all,
):
    """Install MCP for Windsurf IDE."""
    return _install_single_ide(
        ctx,
        "windsurf",
        overwrite,
        no_instructions,
        dry_run,
        is_global,
        recursive,
        include,
        exclude,
    )


@mcp.command()
@common_options
@click.pass_context
@log_command
def kiro(
    ctx,
    overwrite,
    no_instructions,
    dry_run,
    is_global,
    recursive,
    include,
    exclude,
    force_all,
):
    """Install MCP for Kiro IDE."""
    return _install_single_ide(
        ctx,
        "kiro",
        overwrite,
        no_instructions,
        dry_run,
        is_global,
        recursive,
        include,
        exclude,
    )


@mcp.command()
@common_options
@click.pass_context
@log_command
def gemini(
    ctx,
    overwrite,
    no_instructions,
    dry_run,
    is_global,
    recursive,
    include,
    exclude,
    force_all,
):
    """Install MCP for Gemini CLI."""
    return _install_single_ide(
        ctx,
        "gemini",
        overwrite,
        no_instructions,
        dry_run,
        is_global,
        recursive,
        include,
        exclude,
    )


@mcp.command()
@common_options
@click.pass_context
@log_command
def roo(
    ctx,
    overwrite,
    no_instructions,
    dry_run,
    is_global,
    recursive,
    include,
    exclude,
    force_all,
):
    """Install MCP for Roo Code."""
    return _install_single_ide(
        ctx,
        "roo",
        overwrite,
        no_instructions,
        dry_run,
        is_global,
        recursive,
        include,
        exclude,
    )


@mcp.command(name="claude")
@common_options
@click.pass_context
@log_command
def claude(
    ctx,
    overwrite,
    no_instructions,
    dry_run,
    is_global,
    recursive,
    include,
    exclude,
    force_all,
):
    """Install MCP for Claude Code."""
    # The claude command just invokes claude-code
    exit_code = ctx.invoke(
        claude_code,
        overwrite=overwrite,
        no_instructions=no_instructions,
        dry_run=dry_run,
        is_global=is_global,
        recursive=recursive,
        include=include,
        exclude=exclude,
    )
    return exit_code


@mcp.command(name="claude-code", hidden=True)
@common_options
@click.pass_context
@log_command
def claude_code(
    ctx,
    overwrite,
    no_instructions,
    dry_run,
    is_global,
    recursive,
    include,
    exclude,
    force_all,
):
    """Install MCP for Claude Code."""
    return _install_single_ide(
        ctx,
        "claude-code",
        overwrite,
        no_instructions,
        dry_run,
        is_global,
        recursive,
        include,
        exclude,
    )


@mcp.command()
@common_options
@click.pass_context
def vscode(
    ctx,
    overwrite,
    no_instructions,
    dry_run,
    is_global,
    recursive,
    include,
    exclude,
    force_all,
):
    """Install MCP for Visual Studio Code."""
    return _install_single_ide(
        ctx,
        "vscode",
        overwrite,
        no_instructions,
        dry_run,
        is_global,
        recursive,
        include,
        exclude,
    )


@mcp.command()
@common_options
@click.pass_context
@log_command
def amazonq(
    ctx,
    overwrite,
    no_instructions,
    dry_run,
    is_global,
    recursive,
    include,
    exclude,
    force_all,
):
    """Install MCP for Amazon Q Developer."""
    return _install_single_ide(
        ctx,
        "amazonq",
        overwrite,
        no_instructions,
        dry_run,
        is_global,
        recursive,
        include,
        exclude,
    )
