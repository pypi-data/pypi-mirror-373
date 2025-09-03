"""Install command group for zenable-mcp."""

import signal
import sys

import click

from zenable_mcp.commands.install.hook import all_hooks, hook
from zenable_mcp.commands.install.mcp import all_ides, mcp
from zenable_mcp.exit_codes import ExitCode
from zenable_mcp.logging.command_logger import log_command
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.utils.cli_validators import handle_exit_code
from zenable_mcp.utils.config_manager import cleanup_temp_files
from zenable_mcp.utils.context_helpers import get_is_global_from_context
from zenable_mcp.utils.install_report import (
    filter_git_repositories,
    show_complete_filtering_information,
    show_filtering_results,
)
from zenable_mcp.utils.recursive_operations import (
    display_aggregated_results,
    find_git_repositories,
)


def signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    echo("\n⚠️  Installation interrupted by user", err=True, log=True)
    cleanup_temp_files()
    sys.exit(ExitCode.USER_INTERRUPT)


@click.group(
    invoke_without_command=True,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview what would be done without actually performing the installation",
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
def install(ctx, dry_run, recursive, is_global, include, exclude, force_all):
    """Install the Zenable integrations"""
    # Set up signal handler for graceful interruption
    signal.signal(signal.SIGINT, signal_handler)
    # Also handle SIGTERM for completeness
    signal.signal(signal.SIGTERM, signal_handler)

    # Validate that --include and --exclude require --recursive
    if (include or exclude) and not recursive:
        echo(
            click.style("Error: ", fg="red", bold=True)
            + "--include and --exclude options require --recursive to be set",
            err=True,
        )
        return handle_exit_code(ctx, ExitCode.INVALID_PARAMETERS)

    # Store dry_run, global, recursive, and patterns in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["dry_run"] = dry_run
    ctx.obj["is_global"] = is_global
    ctx.obj["recursive"] = recursive
    ctx.obj["include_patterns"] = list(include) if include else None
    ctx.obj["exclude_patterns"] = list(exclude) if exclude else None
    ctx.obj["force_all"] = force_all

    # If recursive, find repositories once and store them in context
    if recursive:
        git_repos = find_git_repositories()

        # Check if no repositories found
        if not git_repos:
            echo("No git repositories found in the current directory or below.")
            return handle_exit_code(ctx, ExitCode.SUCCESS)

        # Apply filtering if patterns are provided
        filter_result = filter_git_repositories(
            git_repos,
            include_patterns=list(include) if include else None,
            exclude_patterns=list(exclude) if exclude else None,
            handler_name="recursive install",
        )

        # Check if all repositories were filtered out
        if include or exclude:
            if len(filter_result.filtered_repos) == 0:
                show_filtering_results(
                    filter_result.original_count,
                    include_patterns=list(include) if include else None,
                    exclude_patterns=list(exclude) if exclude else None,
                )
                return handle_exit_code(ctx, ExitCode.SUCCESS)

        ctx.obj["git_repos"] = filter_result.filtered_repos
        ctx.obj["original_repo_count"] = filter_result.original_count
        ctx.obj["filtered"] = include or exclude

    # If no subcommand is provided, run both mcp all and hook all
    if ctx.invoked_subcommand is None:
        if recursive:
            # Handle recursive installation with aggregated output
            git_repos = ctx.obj.get("git_repos", [])
            if git_repos:
                echo("Installing all of the Zenable integrations recursively...")

                # Show complete filtering information
                original_count = ctx.obj.get("original_repo_count", len(git_repos))
                was_filtered = ctx.obj.get("filtered", False)

                if not show_complete_filtering_information(
                    git_repos,
                    original_count,
                    was_filtered,
                    include_patterns=ctx.obj.get("include_patterns"),
                    exclude_patterns=ctx.obj.get("exclude_patterns"),
                    dry_run=dry_run,
                    ask_confirmation=True,
                ):
                    return handle_exit_code(ctx, ExitCode.SUCCESS)

            if dry_run:
                echo(
                    "\n"
                    + click.style("DRY RUN MODE:", fg="yellow", bold=True)
                    + " Showing what would be done\n"
                )

            # Set flag so subcommands know they're being called from parent
            ctx.obj["from_parent_install"] = True

            # Call subcommands and get results
            mcp_results = ctx.invoke(
                all_ides,
                overwrite=False,
                no_instructions=True,
                dry_run=dry_run,
                recursive=recursive,
                is_global=is_global,
                include=include,
                exclude=exclude,
                force_all=force_all,
            )
            hook_results = ctx.invoke(
                all_hooks,
                is_global=is_global,
                dry_run=dry_run,
                recursive=recursive,
                include=include,
                exclude=exclude,
            )

            # Ensure results are lists
            if not isinstance(mcp_results, list):
                mcp_results = []
            if not isinstance(hook_results, list):
                hook_results = []

            # Display aggregated results
            display_aggregated_results(
                mcp_results=mcp_results,
                hook_results=hook_results,
                dry_run=dry_run,
            )

            # Calculate exit code
            all_results = []
            if mcp_results:
                all_results.extend(mcp_results)
            if hook_results:
                all_results.extend(hook_results)

            failed_count = sum(1 for _, r in all_results if r.is_error)
            exit_code = (
                ExitCode.INSTALLATION_ERROR if failed_count > 0 else ExitCode.SUCCESS
            )

            # Exit with the appropriate code
            return handle_exit_code(ctx, exit_code)
        else:
            # Non-recursive installation
            if not dry_run:
                # Check if we're being called with --global from parent
                is_global = get_is_global_from_context(ctx)
                if is_global:
                    echo("Installing all of the Zenable integrations globally...")
                else:
                    echo("Installing all of the Zenable integrations...")

            ctx.invoke(
                mcp,
                dry_run=dry_run,
                recursive=recursive,
                is_global=is_global,
                include=include,
                exclude=exclude,
                force_all=force_all,
            )
            ctx.invoke(
                hook,
                dry_run=dry_run,
                recursive=recursive,
                include=include,
                exclude=exclude,
            )


install.add_command(hook)
install.add_command(mcp)

# Export signal_handler for testing
__all__ = ["install", "mcp", "signal_handler"]
