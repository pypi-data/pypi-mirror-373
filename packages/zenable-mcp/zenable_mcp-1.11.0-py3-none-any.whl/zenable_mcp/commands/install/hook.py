"""Hook installation commands for zenable-mcp."""

import re
import sys
from pathlib import Path
from typing import Optional

import click

from zenable_mcp import __version__
from zenable_mcp.exit_codes import ExitCode
from zenable_mcp.ide_config import ClaudeCodeConfig
from zenable_mcp.logging.command_logger import log_command
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona
from zenable_mcp.utils.cli_validators import (
    handle_exit_code,
    validate_mutual_exclusivity,
)
from zenable_mcp.utils.config_manager import (
    backup_config_file,
    load_json_config,
    safe_write_json,
)
from zenable_mcp.utils.context_helpers import (
    get_dry_run_from_context,
    get_git_repos_from_context,
    get_recursive_from_context,
)
from zenable_mcp.utils.install_report import (
    filter_git_repositories,
    show_complete_filtering_information,
    show_filtering_results,
)
from zenable_mcp.utils.install_status import (
    InstallResult,
    InstallStatus,
    show_installation_summary,
)
from zenable_mcp.utils.operation_status import OperationStatus
from zenable_mcp.utils.recursive_operations import (
    execute_in_git_repositories,
    find_git_repositories,
)

# Supported matchers for the zenable-mcp hook
SUPPORTED_MATCHERS = ["Write", "Edit", "MultiEdit"]

# Semver pattern for matching version strings in package specifications
SEMVER_PATTERN = re.compile(
    r"@(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?(?:\+[a-zA-Z0-9.-]+)?)"
)


def _load_claude_settings(settings_path: Path) -> dict:
    """Load Claude settings file, handling common edge cases.

    Args:
        settings_path: Path to the Claude settings file

    Returns:
        Dictionary of settings, or empty dict if file doesn't exist

    Raises:
        click.ClickException: If file exists but cannot be read/parsed
    """
    if not settings_path.exists():
        return {}

    try:
        data, _ = load_json_config(settings_path)
        return data
    except (ValueError, IOError) as e:
        echo(f"Failed to load Claude settings from {settings_path}: {e}", err=True)
        sys.exit(ExitCode.FILE_READ_ERROR)


def is_supported_matcher_config(matcher: str) -> bool:
    """Check if a matcher configuration is supported for zenable-mcp.

    Args:
        matcher: The matcher string to check

    Returns:
        True if the matcher contains only Write, Edit, and/or MultiEdit (in any order)
    """
    if not isinstance(matcher, str):
        return False

    parts = [part.strip() for part in matcher.split("|")]
    # Remove empty parts
    parts = [p for p in parts if p]

    # Check if all parts are in SUPPORTED_MATCHERS
    return all(part in SUPPORTED_MATCHERS for part in parts) and len(parts) > 0


def get_settings_path(is_global: bool) -> Path:
    """Determine the appropriate settings file path using IDE capabilities.

    Args:
        is_global: Whether to use global settings

    Returns:
        Path to the settings file

    Raises:
        click.ClickException: If local install but not in a git repository
    """
    try:
        config = ClaudeCodeConfig(is_global=is_global)
        settings_path = config.get_default_hook_config_path()
        if not settings_path:
            if not is_global:
                echo(
                    "Not in a git repository.\n"
                    "Did you mean to do the global installation with --global?",
                    err=True,
                )
            else:
                echo("No hook configuration path available", err=True)
            sys.exit(ExitCode.INSTALLATION_ERROR)
        return settings_path
    except ValueError as e:
        echo(str(e), err=True)
        sys.exit(ExitCode.INSTALLATION_ERROR)


def load_or_create_settings(settings_path: Path) -> tuple[dict, bool]:
    """Load existing settings or create new empty settings.

    Args:
        settings_path: Path to the settings file

    Returns:
        Tuple of (Dictionary of settings, has_comments flag)

    Raises:
        click.ClickException: If JSON is invalid
    """
    if settings_path.exists() and settings_path.stat().st_size > 0:
        try:
            data, has_comments = load_json_config(settings_path)
            return data, has_comments
        except (ValueError, IOError) as e:
            echo(
                f"Failed to load settings from {settings_path}\n"
                f"Details: {e}\n"
                f"Please fix the JSON syntax or backup and remove the file.",
                err=True,
            )
            sys.exit(ExitCode.FILE_READ_ERROR)
    return {}, False


def prompt_for_comment_warning(
    settings_path: Path, dry_run: bool = False
) -> tuple[bool, Optional[Path]]:
    """Prompt user to confirm modification of a JSON file with comments.

    Args:
        settings_path: Path to the settings file that has comments
        dry_run: If True, always return True without prompting

    Returns:
        Tuple of (True if user confirms or dry_run is True, backup path if created)
    """
    if dry_run:
        return True, None

    # Create backup first
    backup_path = backup_config_file(settings_path)

    echo(
        click.style("\n⚠️  Warning: ", fg="yellow", bold=True)
        + f"The file {settings_path} contains comments or JSON5 features.\n"
        "These comments will be LOST when the file is saved.\n"
        f"\nA backup has been created at: {backup_path}"
    )

    confirmed = click.confirm(
        "Do you want to proceed with the modification?", default=False
    )
    return confirmed, backup_path if confirmed else None


def ensure_hook_structure(settings: dict) -> None:
    """Ensure the settings have the required hook structure.

    Args:
        settings: Settings dictionary to update in place
    """
    settings.setdefault("hooks", {})
    settings["hooks"].setdefault("PostToolUse", [])


def create_hook_config(matcher: str = None) -> dict:
    """Create a standard hook configuration.

    Args:
        matcher: Optional custom matcher string. If None, uses default supported matchers.

    Returns:
        Hook configuration dictionary
    """
    if matcher is None:
        matcher = "|".join(SUPPORTED_MATCHERS)

    return {
        "matcher": matcher,
        "hooks": [{"type": "command", "command": "uvx zenable-mcp@latest hook"}],
    }


def should_update_matcher(matcher: str) -> bool:
    """Check if a matcher should be updated to include Write, Edit, and MultiEdit.

    Args:
        matcher: The matcher string to check

    Returns:
        True if the matcher should be updated
    """
    if not isinstance(matcher, str):
        return False

    parts = [part.strip() for part in matcher.split("|")]
    has_edit = "Edit" in parts
    has_write = "Write" in parts
    has_multiedit = "MultiEdit" in parts

    # Already has all three, no update needed
    if has_write and has_edit and has_multiedit:
        return False

    # Count how many of our supported matchers are present
    supported_count = sum([has_write, has_edit, has_multiedit])

    # If it has at least one of our matchers but not all
    if supported_count > 0 and supported_count < 3:
        # Check if there are any non-supported matchers
        non_supported_matchers = [p for p in parts if p not in SUPPORTED_MATCHERS]

        # Only update if there's at most 1 non-supported matcher
        # This allows updating "Write|Read" or "Edit|Bash" but not "Edit|Foo|Bar|Write"
        if len(non_supported_matchers) <= 1:
            return True

    return False


def extract_command_from_hook(hook: dict) -> str:
    """Extract the command from a hook configuration.

    Args:
        hook: Hook configuration dictionary

    Returns:
        Command string or empty string if not found
    """
    if isinstance(hook, dict) and "hooks" in hook:
        for sub_hook in hook.get("hooks", []):
            if isinstance(sub_hook, dict) and sub_hook.get("type") == "command":
                return sub_hook.get("command", "")
    return ""


def analyze_existing_hooks(post_tool_use: list, new_hook_config: dict) -> dict:
    """Analyze existing hooks for duplicates and similar configurations.

    Args:
        post_tool_use: List of existing PostToolUse hooks
        new_hook_config: The new hook configuration to check against

    Returns:
        Dictionary with analysis results
    """
    result = {
        "hook_exists": False,
        "has_latest": False,
        "similar_hook_indices": [],
        "pinned_version_indices": [],
        "matcher_update_indices": [],
    }

    for i, existing_hook in enumerate(post_tool_use):
        if existing_hook == new_hook_config:
            result["hook_exists"] = True
            break

        command = extract_command_from_hook(existing_hook)

        if command.startswith("uvx zenable-mcp"):
            matcher = existing_hook.get("matcher", "")

            if not is_supported_matcher_config(matcher):
                echo(
                    f"⚠️  Warning: Hook with matcher '{matcher}' is not a supported configuration for zenable-mcp.\n"
                    f"   Supported configuration should only contain {' and '.join(SUPPORTED_MATCHERS)}.\n"
                    f"   The check may not behave as expected.",
                    err=True,
                )

            if (
                should_update_matcher(matcher)
                and i not in result["matcher_update_indices"]
            ):
                result["matcher_update_indices"].append(i)

            if "@latest" in command:
                result["has_latest"] = True
            elif SEMVER_PATTERN.search(command):
                result["pinned_version_indices"].append(i)
            elif command != "uvx zenable-mcp@latest hook":
                result["similar_hook_indices"].append(i)

    return result


def update_hook_matcher(hook: dict, new_matcher: str = None) -> dict:
    """Update a hook's matcher to include Write, Edit, and MultiEdit.

    Args:
        hook: Hook configuration to update
        new_matcher: Optional new matcher. If None, updates existing.

    Returns:
        Updated hook configuration
    """
    if new_matcher:
        hook["matcher"] = new_matcher
    else:
        old_matcher = hook.get("matcher", "")
        parts = [part.strip() for part in old_matcher.split("|")]
        if "Write" not in parts:
            parts.append("Write")
        if "Edit" not in parts:
            parts.append("Edit")
        if "MultiEdit" not in parts:
            parts.append("MultiEdit")
        hook["matcher"] = "|".join(parts)

    return hook


def save_settings_with_confirmation(
    settings_path: Path, settings: dict, has_comments: bool, dry_run: bool
) -> tuple[bool, Optional[Path]]:
    """Save settings with confirmation if file has comments.

    Args:
        settings_path: Path to save settings to
        settings: Settings dictionary to save
        has_comments: Whether the file has comments
        dry_run: Whether this is a dry run

    Returns:
        Tuple of (success, backup_path)
    """
    if dry_run:
        return True, None

    backup_path = None
    if has_comments:
        confirmed, backup_path = prompt_for_comment_warning(settings_path, dry_run)
        if not confirmed:
            return False, None

    safe_write_json(settings_path, settings)
    return True, backup_path


def handle_pinned_versions(
    post_tool_use: list,
    pinned_version_indices: list,
    settings_path: Path,
    settings: dict,
    has_comments: bool,
    dry_run: bool,
) -> Optional[InstallResult]:
    """Handle updating pinned version hooks to @latest.

    Returns:
        InstallResult if handled, None otherwise
    """
    if not pinned_version_indices:
        return None

    updated = False
    old_version = "unknown"

    for idx in pinned_version_indices:
        old_hook = post_tool_use[idx]
        old_command = ""
        if isinstance(old_hook, dict) and "hooks" in old_hook:
            for sub_hook in old_hook.get("hooks", []):
                if isinstance(sub_hook, dict) and sub_hook.get("type") == "command":
                    old_command = sub_hook.get("command", "")
                    break

        # Extract the version from the command
        version_match = SEMVER_PATTERN.search(old_command)
        old_version = version_match.group(1) if version_match else "unknown"

        old_matcher = old_hook.get("matcher", "")
        if should_update_matcher(old_matcher):
            # Update the existing hook to add missing matchers
            updated_hook = update_hook_matcher(old_hook.copy())
            # Update the command to the latest
            for sub_hook in updated_hook.get("hooks", []):
                if isinstance(sub_hook, dict) and sub_hook.get("type") == "command":
                    sub_hook["command"] = "uvx zenable-mcp@latest hook"
            post_tool_use[idx] = updated_hook
        else:
            post_tool_use[idx] = create_hook_config(old_matcher)
        updated = True

    if updated:
        success, _ = save_settings_with_confirmation(
            settings_path, settings, has_comments, dry_run
        )
        if not success:
            return InstallResult(
                InstallStatus.CANCELLED,
                "Claude Code hook",
                "Installation cancelled",
            )

        # Return success with appropriate message
        if old_version != __version__:
            message = f"Updated hook from pinned version ({old_version}) to @latest (current: {__version__})"
        else:
            message = f"Updated hook from pinned version ({old_version}) to @latest"

        return InstallResult(InstallStatus.SUCCESS, "Claude Code hook", message)

    return None


def handle_similar_hooks(
    post_tool_use: list,
    similar_hook_indices: list,
    settings_path: Path,
    settings: dict,
    has_comments: bool,
    dry_run: bool,
) -> Optional[InstallResult]:
    """Handle updating similar hooks.

    Returns:
        InstallResult if handled, None otherwise
    """
    if not similar_hook_indices:
        return None

    # Update similar hooks
    for idx in reversed(
        similar_hook_indices
    ):  # Reverse to maintain indices while removing
        old_hook = post_tool_use[idx]
        old_matcher = old_hook.get("matcher", "")

        if should_update_matcher(old_matcher):
            # Update the existing hook to add missing matchers
            updated_hook = update_hook_matcher(old_hook.copy())
            # Update the command to the latest
            for sub_hook in updated_hook.get("hooks", []):
                if isinstance(sub_hook, dict) and sub_hook.get("type") == "command":
                    sub_hook["command"] = "uvx zenable-mcp@latest hook"
            post_tool_use[idx] = updated_hook
        else:
            post_tool_use[idx] = create_hook_config(old_matcher)

    success, _ = save_settings_with_confirmation(
        settings_path, settings, has_comments, dry_run
    )
    if not success:
        return InstallResult(
            InstallStatus.CANCELLED,
            "Claude Code hook",
            "Installation cancelled",
        )

    return InstallResult(
        InstallStatus.SUCCESS,
        "Claude Code hook",
        "Updated existing hook to 'uvx zenable-mcp@latest check'",
    )


def handle_matcher_updates(
    post_tool_use: list,
    matcher_update_indices: list,
    pinned_version_indices: list,
    similar_hook_indices: list,
    settings_path: Path,
    settings: dict,
    has_comments: bool,
    dry_run: bool,
) -> Optional[InstallResult]:
    """Handle updating matchers for hooks.

    Returns:
        InstallResult if handled, None otherwise
    """
    # Remove any indices that were already handled in pinned_version_indices or similar_hook_indices
    remaining_matcher_indices = [
        idx
        for idx in matcher_update_indices
        if idx not in pinned_version_indices and idx not in similar_hook_indices
    ]

    if not remaining_matcher_indices:
        return None

    updated_matchers = []
    for idx in remaining_matcher_indices:
        old_hook = post_tool_use[idx]
        old_matcher = old_hook.get("matcher", "")

        post_tool_use[idx] = update_hook_matcher(post_tool_use[idx])

        # Also update the command if needed
        for sub_hook in post_tool_use[idx].get("hooks", []):
            if isinstance(sub_hook, dict) and sub_hook.get("type") == "command":
                old_command = sub_hook.get("command", "")
                if (
                    old_command.startswith("uvx zenable-mcp")
                    and old_command != "uvx zenable-mcp@latest hook"
                ):
                    sub_hook["command"] = "uvx zenable-mcp@latest hook"

        new_matcher = post_tool_use[idx]["matcher"]
        updated_matchers.append(f"'{old_matcher}' → '{new_matcher}'")

    success, _ = save_settings_with_confirmation(
        settings_path, settings, has_comments, dry_run
    )
    if not success:
        return InstallResult(
            InstallStatus.CANCELLED,
            "Claude Code hook",
            "Installation cancelled",
        )

    if len(updated_matchers) == 1:
        message = f"Updated matcher from {updated_matchers[0]}"
    else:
        message = f"Updated {len(updated_matchers)} matchers"

    return InstallResult(InstallStatus.SUCCESS, "Claude Code hook", message)


def _install_claude_hook_in_repo(repo_path: Path, dry_run: bool) -> InstallResult:
    """Install Claude Code hook in a specific repository.

    This is used as the operation function for recursive installations.

    Args:
        repo_path: Path to the repository (unused but required by interface)
        dry_run: Whether this is a dry run

    Returns:
        InstallResult with the outcome of the installation
    """
    try:
        return _claude_impl(is_global=False, dry_run=dry_run)
    except SystemExit:
        return InstallResult(InstallStatus.FAILED, "Claude Code hook", "Failed")


def _claude_impl(is_global: bool, dry_run: bool = False):
    """Implementation of claude command with dependency injection.

    Args:
        is_global: Whether to install globally
        dry_run: Whether to show what would be done without making changes

    Returns:
        InstallResult object
    """
    settings_path = get_settings_path(is_global)

    new_hook_config = create_hook_config()

    # Don't print here in dry-run mode - will be handled later
    if not dry_run:
        settings_path.parent.mkdir(parents=True, exist_ok=True)

    settings, has_comments = load_or_create_settings(settings_path)
    ensure_hook_structure(settings)

    # Log the number of existing hooks found
    num_hooks = len(settings["hooks"].get("PostToolUse", []))
    if num_hooks > 0:
        echo(
            f"Found {num_hooks} existing PostToolUse hook(s) in {settings_path}",
            persona=Persona.POWER_USER,
        )
    else:
        echo(
            f"No existing PostToolUse hooks found in {settings_path}",
            persona=Persona.POWER_USER,
        )

    post_tool_use = settings["hooks"]["PostToolUse"]
    analysis = analyze_existing_hooks(post_tool_use, new_hook_config)

    hook_exists = analysis["hook_exists"]
    has_latest = analysis["has_latest"]
    similar_hook_indices = analysis["similar_hook_indices"]
    pinned_version_indices = analysis["pinned_version_indices"]
    matcher_update_indices = analysis["matcher_update_indices"]

    # Check for already installed hooks
    if hook_exists:
        echo(
            f"Claude Code hook already properly installed in {settings_path}",
            persona=Persona.POWER_USER,
        )
        return InstallResult(
            InstallStatus.ALREADY_INSTALLED,
            "Claude Code hook",
            "Hook already installed - no changes needed",
        )

    if has_latest and not matcher_update_indices:
        echo(
            f"Claude Code hook with @latest already installed in {settings_path}",
            persona=Persona.POWER_USER,
        )
        return InstallResult(
            InstallStatus.ALREADY_INSTALLED,
            "Claude Code hook",
            "Hook with @latest already installed - no changes needed",
        )

    # Try handling pinned versions
    result = handle_pinned_versions(
        post_tool_use,
        pinned_version_indices,
        settings_path,
        settings,
        has_comments,
        dry_run,
    )
    if result:
        return result

    # Try handling similar hooks
    result = handle_similar_hooks(
        post_tool_use,
        similar_hook_indices,
        settings_path,
        settings,
        has_comments,
        dry_run,
    )
    if result:
        return result

    # Try handling matcher updates
    result = handle_matcher_updates(
        post_tool_use,
        matcher_update_indices,
        pinned_version_indices,
        similar_hook_indices,
        settings_path,
        settings,
        has_comments,
        dry_run,
    )
    if result:
        return result

    # If no special cases, add new hook
    if matcher_update_indices:
        # All matcher updates were handled by other scenarios, add new hook
        if not dry_run:
            post_tool_use.append(new_hook_config)
            success, _ = save_settings_with_confirmation(
                settings_path, settings, has_comments, dry_run
            )
            if not success:
                return InstallResult(
                    InstallStatus.CANCELLED,
                    "Claude Code hook",
                    "Installation cancelled",
                )
    else:
        # Add new hook
        if not dry_run:
            post_tool_use.append(new_hook_config)
            success, _ = save_settings_with_confirmation(
                settings_path, settings, has_comments, dry_run
            )
            if not success:
                return InstallResult(
                    InstallStatus.CANCELLED,
                    "Claude Code hook",
                    "Installation cancelled",
                )

    return InstallResult(
        InstallStatus.SUCCESS, "Claude Code hook", "Claude Code hook installed"
    )


def _get_claude_global_hook_path() -> Path:
    """Get the Claude Code global hook configuration path.

    Returns:
        Path object for the global hook config
    """
    config = ClaudeCodeConfig(is_global=True)
    return config.get_default_hook_config_path()


# Common options decorator for hook subcommands
def common_hook_options(f):
    """Decorator to add common options to all hook subcommands."""
    f = click.option(
        "--global",
        "-g",
        "is_global",
        is_flag=True,
        default=False,
        help=f"Install globally in {_get_claude_global_hook_path()}",
    )(f)
    f = click.option(
        "--dry-run",
        is_flag=True,
        default=False,
        help="Preview what would be done without actually performing the installation",
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
    return f


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
    "--include",
    multiple=True,
    help="Include only directories matching these glob patterns (e.g., '**/microservice-*')",
)
@click.option(
    "--exclude",
    multiple=True,
    help="Exclude directories matching these glob patterns",
)
@click.pass_context
@log_command
def hook(ctx, dry_run, recursive, include, exclude):
    """Install hooks for various tools.

    \b
    Examples:
      # Install all hooks (default)
      zenable-mcp install hook
      zenable-mcp install hook all
    \b
      # Install Claude hook specifically
      zenable-mcp install hook claude
    \b
      # Preview what would be installed
      zenable-mcp install hook --dry-run
      zenable-mcp install hook claude-code --dry-run

    \b
    For more information, visit:
    https://docs.zenable.io/integrations/mcp/hooks
    """
    # Validate that --include and --exclude require --recursive
    if (include or exclude) and not recursive:
        echo(
            click.style("Error: ", fg="red", bold=True)
            + "--include and --exclude options require --recursive to be set",
            err=True,
        )
        return handle_exit_code(ctx, ExitCode.INVALID_PARAMETERS)

    # Store dry_run, recursive, and patterns in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["dry_run"] = dry_run
    ctx.obj["recursive"] = recursive
    ctx.obj["include_patterns"] = list(include) if include else None
    ctx.obj["exclude_patterns"] = list(exclude) if exclude else None

    # Pass through git_repos from parent context if available
    if ctx.parent and ctx.parent.obj and "git_repos" in ctx.parent.obj:
        ctx.obj["git_repos"] = ctx.parent.obj["git_repos"]

    # If no subcommand is provided, default to 'all'
    if ctx.invoked_subcommand is None:
        # Get parent's recursive flag if available
        if not recursive and ctx.parent and ctx.parent.obj:
            recursive = ctx.parent.obj.get("recursive", False)
        ctx.invoke(all_hooks, recursive=recursive, include=include, exclude=exclude)


@hook.command(name="all")
@common_hook_options
@click.pass_context
@log_command
def all_hooks(ctx, is_global, dry_run, recursive, include, exclude):
    """Install hooks for all supported tools."""
    # Check for mutual exclusivity of --global and --recursive
    validate_mutual_exclusivity(is_global, recursive, "--global", "--recursive")

    # Get flags from context hierarchy if not explicitly set
    if not dry_run:
        dry_run = get_dry_run_from_context(ctx)
    if not recursive:
        recursive = get_recursive_from_context(ctx)

    # Check if we're being called from parent install command
    from_parent_install = ctx.obj and ctx.obj.get("from_parent_install", False)

    if recursive:
        # Run recursively in all git repositories

        # Get repos from context using helper
        git_repos = get_git_repos_from_context(ctx)

        # If still not found, find them now
        if git_repos is None:
            git_repos = find_git_repositories()
            if ctx.obj:
                ctx.obj["git_repos"] = git_repos

        # Get patterns from context if not explicitly provided
        include_patterns = list(include) if include else ctx.obj.get("include_patterns")
        exclude_patterns = list(exclude) if exclude else ctx.obj.get("exclude_patterns")

        # Apply filtering if patterns are provided
        original_count = len(git_repos)
        filter_result = filter_git_repositories(
            git_repos,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            handler_name="recursive hook install",
        )
        git_repos = filter_result.filtered_repos

        if not from_parent_install:
            # Check if all repositories were filtered out
            if (include_patterns or exclude_patterns) and len(git_repos) == 0:
                show_filtering_results(
                    filter_result.original_count,
                    include_patterns=include_patterns,
                    exclude_patterns=exclude_patterns,
                )
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
                return ExitCode.SUCCESS
        elif not from_parent_install and not (include_patterns or exclude_patterns):
            # Only print if not called from parent and no filtering
            # Show simple count without full filtering report
            repo_text = "repository" if len(git_repos) == 1 else "repositories"
            echo(f"\nFound {len(git_repos)} git {repo_text}")

        if not git_repos:
            if not from_parent_install and not (include_patterns or exclude_patterns):
                # Only show message if not filtered (filtering messages shown above)
                echo("No git repositories found in the current directory or below.")
            return OperationStatus.NO_FILES_FOUND

        # Execute the operation across all repositories
        all_results, exit_code = execute_in_git_repositories(
            operation_func=_install_claude_hook_in_repo,
            operation_name="Claude Code hook",
            dry_run=dry_run,
            git_repos=git_repos,  # Use already-found repositories
            silent=from_parent_install,  # Silent when called from parent
        )

        # If called from parent, return results for aggregation
        if from_parent_install:
            return all_results

        return exit_code
    else:
        # Execute the logic - currently only Claude Code is supported
        results = []

        try:
            # Currently only Claude Code is supported
            result = _claude_impl(is_global, dry_run)
            results.append(result)
        except SystemExit:
            if not from_parent_install:
                echo(
                    "Error: Unknown issue while installing the Claude Code hook, please report this at zenable.io/feedback",
                    err=True,
                )
            results.append(
                InstallResult(InstallStatus.FAILED, "Claude Code hook", "Failed")
            )

    # If called from parent, return results for aggregation
    if from_parent_install:
        return results

    # In dry-run mode, display file operations
    if dry_run and any(r.status == InstallStatus.SUCCESS for r in results):
        settings_path = get_settings_path(is_global)
        if settings_path.exists():
            echo(f"\n{click.style('Would modify:', fg='cyan', bold=True)}")
            echo(f"  • {settings_path}")
        else:
            echo(f"\n{click.style('Would create:', fg='cyan', bold=True)}")
            echo(f"  • {settings_path}")

    # Show summary
    show_installation_summary(results, dry_run, "Hooks Installation")

    # In dry-run mode, show preview message
    if dry_run and any(r.is_success for r in results):
        echo(
            "\nTo actually perform the installation, run the command without --dry-run"
        )

    # Return appropriate exit code
    if any(r.is_error for r in results):
        return handle_exit_code(ctx, ExitCode.INSTALLATION_ERROR)
    else:
        return ExitCode.SUCCESS


@hook.command(name="claude-code")
@common_hook_options
@click.pass_context
@log_command
def claude_code_hook(ctx, is_global, dry_run, recursive, include, exclude):
    """Install Claude Code hooks."""
    # Check for mutual exclusivity of --global and --recursive
    validate_mutual_exclusivity(is_global, recursive, "--global", "--recursive")

    # Get flags from context hierarchy if not explicitly set
    if not dry_run:
        dry_run = get_dry_run_from_context(ctx)
    if not recursive:
        recursive = get_recursive_from_context(ctx)

    if recursive:
        # Run recursively - delegate to all_hooks
        return ctx.invoke(
            all_hooks,
            is_global=False,
            dry_run=dry_run,
            recursive=True,
            include=include,
            exclude=exclude,
        )

    results = []

    try:
        result = _claude_impl(is_global, dry_run)
        results.append(result)
    except SystemExit as e:
        echo(f"Error installing Claude Code hook: {e}", err=True)
        results.append(
            InstallResult(InstallStatus.FAILED, "Claude Code hook", "Failed")
        )

    # In dry-run mode, display file operations
    if dry_run and any(r.status == InstallStatus.SUCCESS for r in results):
        settings_path = get_settings_path(is_global)
        if settings_path.exists():
            echo(f"\n{click.style('Would modify:', fg='cyan', bold=True)}")
            echo(f"  • {settings_path}")
        else:
            echo(f"\n{click.style('Would create:', fg='cyan', bold=True)}")
            echo(f"  • {settings_path}")

    # Show summary
    show_installation_summary(results, dry_run, "Hooks Installation")

    # In dry-run mode, show preview message
    if dry_run and any(r.is_success for r in results):
        echo(
            "\nTo actually perform the installation, run the command without --dry-run"
        )

    # Return appropriate exit code
    if any(r.is_error for r in results):
        return handle_exit_code(ctx, ExitCode.INSTALLATION_ERROR)
    else:
        return ExitCode.SUCCESS


@hook.command(name="claude")
@common_hook_options
@click.pass_context
@log_command
def claude(ctx, is_global, dry_run, recursive, include, exclude):
    """Install Claude Code hooks."""
    # Just invoke claude-code
    ctx.invoke(
        claude_code_hook,
        is_global=is_global,
        dry_run=dry_run,
        recursive=recursive,
        include=include,
        exclude=exclude,
    )
