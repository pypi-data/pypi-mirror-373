"""Utilities for recursive operations across git repositories."""

import os
from pathlib import Path
from typing import Callable, Optional

import click
from git import InvalidGitRepositoryError, NoSuchPathError, Repo

from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona
from zenable_mcp.utils.install_status import InstallResult, InstallStatus
from zenable_mcp.utils.operation_status import OperationStatus


def find_git_repositories(
    start_path: Optional[Path] = None, max_depth: int = 5
) -> list[Path]:
    """Find all git repositories below the given path.

    This function searches for directories containing a .git folder,
    indicating they are git repositories. It does not search within
    nested git repositories (e.g., submodules).

    If the start path itself is within a git repository, that repository will be
    included in the results and the search will continue from there.

    Args:
        start_path: The path to start searching from. Defaults to current directory.
        max_depth: Maximum depth to search for repositories.

    Returns:
        List of paths to git repository roots
    """
    if start_path is None:
        start_path = Path.cwd()

    git_repos = []

    # First, check if we're currently inside a git repository
    try:
        repo = Repo(start_path, search_parent_directories=True)
        repo_root = Path(repo.git.rev_parse("--show-toplevel"))

        # Add the current repository to the list
        echo(
            f"Current directory is within git repository: {repo_root}",
            persona=Persona.POWER_USER,
        )
        git_repos.append(repo_root)

    except (InvalidGitRepositoryError, NoSuchPathError, OSError):
        # Not in a git repository, proceed to search below
        echo(
            "Current directory is not within a git repository",
            persona=Persona.DEVELOPER,
        )

    # Track visited directories to avoid duplicates
    visited_repos = set()
    if git_repos:
        visited_repos.add(str(git_repos[0]))

    # Track if we actually hit the depth limit with potential repositories to explore
    hit_depth_limit = False

    # Walk the directory tree looking for .git directories
    for root, dirs, _ in os.walk(start_path):
        current_path = Path(root)

        # Calculate depth from start_path
        try:
            relative_depth = len(current_path.relative_to(start_path).parts)
        except ValueError:
            # If current_path is not relative to start_path, skip it
            continue

        # Check if we're approaching the depth limit
        if relative_depth == max_depth - 1:
            # We're one level before max_depth, check if we have subdirectories
            # that we won't explore (they would be at max_depth)
            if dirs:
                # Filter out .git since we're already in a repo if it exists
                non_git_dirs = [d for d in dirs if d != ".git"]
                if non_git_dirs:
                    hit_depth_limit = True

        # Stop if we've reached max depth
        if relative_depth >= max_depth:
            dirs.clear()  # Don't recurse deeper
            continue

        # Check if this is a git repository
        if ".git" in dirs:
            # Check if this is a valid git repository using gitpython
            try:
                repo = Repo(current_path)
                repo_root_str = str(current_path.resolve())

                # Only add if we haven't seen this repository before
                if repo_root_str not in visited_repos:
                    git_repos.append(current_path)
                    visited_repos.add(repo_root_str)
                    echo(
                        f"Found git repository: {current_path}",
                        persona=Persona.POWER_USER,
                    )

                # Don't search within this git repository for nested ones
                dirs.clear()
            except (InvalidGitRepositoryError, NoSuchPathError, OSError):
                # Not a valid git repository, continue searching
                pass

    # Only warn if we actually hit the depth limit with subdirectories to explore
    if hit_depth_limit:
        echo(
            f"Directory traversal limited to {max_depth} levels deep. Some repositories may have been skipped.",
            persona=Persona.USER,
            err=True,
        )

    return git_repos


def execute_in_git_repositories(
    operation_func: Callable[[Path, bool], InstallResult],
    operation_name: str,
    dry_run: bool = False,
    start_path: Optional[Path] = None,
    silent: bool = False,
    git_repos: Optional[list[Path]] = None,
) -> tuple[list[tuple[Path, InstallResult]], int]:
    """Execute an operation in all git repositories below the start path.

    This function handles:
    - Finding git repositories (or using provided list)
    - Changing to each repository directory
    - Executing the operation
    - Restoring the original directory
    - Displaying progress and results
    - Calculating exit codes

    Args:
        operation_func: Function to execute in each repository.
                       Takes (repo_path, dry_run) and returns InstallResult
        operation_name: Name of the operation for display purposes
        dry_run: Whether this is a dry run
        start_path: The path to start searching from. Defaults to current directory.
        silent: If True, suppress output and just return results
        git_repos: Optional list of already-found git repositories to use instead of searching

    Returns:
        Tuple of (results list, exit code)
        Results list contains tuples of (repo_path, InstallResult)
    """
    # Use provided repositories or find them
    if git_repos is None:
        git_repos = find_git_repositories(start_path)

    if not git_repos:
        if not silent:
            echo("No git repositories found in the current directory or below.")
        return [], OperationStatus.NO_FILES_FOUND

    # Don't print "Found X git repositories" here - let the caller handle it
    for repo in git_repos:
        echo(f"Repository found: {repo}", persona=Persona.POWER_USER)

    if dry_run and not silent:
        echo(
            "\n"
            + click.style("DRY RUN MODE:", fg="yellow", bold=True)
            + " Showing what would be done\n"
        )

    all_results = []
    original_cwd = os.getcwd()

    for repo in git_repos:
        # Get repository name from path
        repo_name = repo.name

        # Show what we're doing in this repository
        if not silent:
            # Format the operation name for display (add "the" and pluralize "hook" to "hooks")
            display_name = operation_name
            if "hook" in operation_name.lower():
                display_name = "the " + operation_name.replace(" hook", " hooks")

            if dry_run:
                echo(
                    f"\n{click.style('→', fg='cyan')} Would configure {display_name} in the {repo_name} repository"
                )
            else:
                echo(f"\nConfiguring {display_name} in the {repo_name} repository...")

        # Change to the repository directory and execute operation
        try:
            os.chdir(repo)
            result = operation_func(repo, dry_run)
            all_results.append((repo, result))
            # Display result for this repository
            if not silent:
                _display_repository_result(result, dry_run)

        except (OSError, IOError, PermissionError) as e:
            # Handle file system and permission errors
            echo(
                f"Failed to process repository {repo}: {e}",
                persona=Persona.DEVELOPER,
                err=True,
            )
            error_result = InstallResult(
                status=InstallStatus.FAILED,
                component_name=operation_name,
                message=f"Failed: {e}",
            )
            all_results.append((repo, error_result))
            if not silent:
                echo(f"  {click.style('✗', fg='red')} Failed: {e}")

        except Exception as e:
            # Handle any other exceptions that may occur
            echo(
                f"Unexpected error in repository {repo}: {e}",
                persona=Persona.DEVELOPER,
                err=True,
            )
            error_result = InstallResult(
                status=InstallStatus.FAILED,
                component_name=operation_name,
                message=f"{e}",
            )
            all_results.append((repo, error_result))
            if not silent:
                echo(f"  {click.style('✗', fg='red')} Error: {e}")

        finally:
            # Always restore the original directory
            try:
                os.chdir(original_cwd)
            except OSError:
                # If we can't change back, at least log it
                echo(
                    f"Failed to restore working directory to {original_cwd}",
                    persona=Persona.DEVELOPER,
                    err=True,
                )

    # Show overall summary
    if not silent:
        _display_overall_summary(all_results, dry_run)

    # Calculate exit code
    failed_count = sum(1 for _, r in all_results if r.is_error)
    return all_results, 1 if failed_count > 0 else 0


def execute_for_multiple_components(
    paths: list[Path],
    components: list[str],
    operation_func: Callable[[Path, str, bool], InstallResult],
    dry_run: bool = False,
    component_type: str = "IDEs",
    silent: bool = False,
) -> list[tuple[Path, InstallResult]]:
    """Execute an operation for multiple components in multiple paths.

    This is a helper for cases where you need to install multiple IDEs
    or run multiple operations per path.

    Args:
        paths: List of paths (typically repository paths)
        components: List of component names (e.g., IDE names)
        operation_func: Function that takes (path, component_name, dry_run)
                       and returns InstallResult
        dry_run: Whether this is a dry run
        component_type: Type of components being installed (for display)
        silent: If True, suppress output and just return results

    Returns:
        List of tuples of (path, InstallResult)
    """
    all_results = []
    original_cwd = os.getcwd()

    for path in paths:
        # Get repository name from path
        repo_name = path.name

        # For now, always display all components
        display_components = components

        # Format component names for display
        component_names = _format_component_list(display_components)

        # Add "the" and pluralize "hooks" if all components are hooks
        if all("hook" in comp.lower() for comp in display_components):
            # Remove "hook" from each component and add "hooks" at the end
            cleaned_components = [
                comp.replace(" hook", "").replace(" Hook", "")
                for comp in display_components
            ]
            component_names = (
                "the " + _format_component_list(cleaned_components) + " hooks"
            )

        # Show what we're installing in this repository
        if not silent:
            if dry_run:
                echo(
                    f"\n{click.style('→', fg='cyan')} Would configure {component_names} in the {repo_name} repository"
                )
            else:
                echo(
                    f"\nConfiguring {component_names} in the {repo_name} repository..."
                )

        path_results = []

        try:
            os.chdir(path)

            # Execute operation for each component in this path
            for component in components:
                try:
                    result = operation_func(path, component, dry_run)
                    path_results.append(result)
                    all_results.append((path, result))
                except (OSError, IOError, PermissionError) as e:
                    # Handle file system and permission errors for individual components
                    error_result = InstallResult(
                        status=InstallStatus.FAILED,
                        component_name=component,
                        message=f"Failed: {e}",
                    )
                    path_results.append(error_result)
                    all_results.append((path, error_result))

            # Display summary for this repository
            if not silent:
                _display_repo_summary(path_results, dry_run)

        except OSError as e:
            # Handle directory change failures
            echo(
                f"Failed to change to path {path}: {e}",
                persona=Persona.DEVELOPER,
                err=True,
            )
            # Create error results for all components if we can't change directory
            for component in components:
                error_result = InstallResult(
                    status=InstallStatus.FAILED,
                    component_name=component,
                    message=f"Failed to access path: {e}",
                )
                all_results.append((path, error_result))
            if not silent:
                echo(f"  {click.style('✗', fg='red')} Failed to access repository: {e}")

        finally:
            # Always restore the original directory
            try:
                os.chdir(original_cwd)
            except OSError:
                # If we can't change back, at least log it
                echo(
                    f"Failed to restore working directory to {original_cwd}",
                    persona=Persona.DEVELOPER,
                    err=True,
                )

    return all_results


# ============================================================================
# Display Helper Functions
# ============================================================================


def _format_component_list(components: list[str]) -> str:
    """Format a list of components for display.

    Args:
        components: List of component names

    Returns:
        Formatted string like "Foo", "Foo and Bar", or "Foo, Bar, and Baz"
    """
    if not components:
        return ""
    elif len(components) == 1:
        return components[0]
    elif len(components) == 2:
        return f"{components[0]} and {components[1]}"
    else:
        return ", ".join(components[:-1]) + f", and {components[-1]}"


def _get_component_type(results: list[InstallResult]) -> tuple[str, str]:
    """Determine the type of components from results.

    Returns:
        Tuple of (plural_form, singular_form)
    """
    if results and "hook" in results[0].component_name.lower():
        return "hooks", "hook"
    return "IDEs", "IDE"


def _categorize_results(results: list[InstallResult]) -> dict[str, list[InstallResult]]:
    """Categorize results by their status.

    Returns:
        Dictionary with keys 'success', 'already', 'failed'
    """
    return {
        "success": [
            r
            for r in results
            if r.is_success and r.status != InstallStatus.ALREADY_INSTALLED
        ],
        "already": [r for r in results if r.status == InstallStatus.ALREADY_INSTALLED],
        "failed": [r for r in results if r.is_error],
    }


def _display_status_line(
    icon: str,
    color: str,
    count: int,
    component_type: str,
    component_type_singular: str,
    action: str,
    names: list[str] = None,
    max_names: int = 3,
) -> None:
    """Display a single status line with proper formatting.

    Args:
        icon: Icon to display (✓, →, ✗, etc.)
        color: Color for the icon
        count: Number of items
        component_type: Plural form of component type
        component_type_singular: Singular form of component type
        action: Action text (e.g., "configured", "already configured", "would fail")
        names: Optional list of component names to display
        max_names: Maximum number of names to display inline
    """
    type_str = component_type_singular if count == 1 else component_type

    if names and len(names) <= max_names:
        names_str = _format_component_list(names)
        # Always use the action format for consistency
        echo(f"  {click.style(icon, fg=color)} {action} {names_str}")
    else:
        # For larger lists, show count with type
        if "Would configure" in action or "Configured" == action:
            echo(f"  {click.style(icon, fg=color)} {action} {count} {type_str}")
        else:
            echo(f"  {click.style(icon, fg=color)} {count} {type_str} {action}")


def _display_failures(
    failed_results: list[InstallResult], max_display: int = 5
) -> None:
    """Display failure details with a limit.

    Args:
        failed_results: List of failed results
        max_display: Maximum number of failures to display
    """
    for i, result in enumerate(failed_results[:max_display]):
        echo(f"    - {result.component_name}: {result.message}")

    if len(failed_results) > max_display:
        remaining = len(failed_results) - max_display
        echo(
            f"    ...and {remaining} additional failure{'s' if remaining != 1 else ''}"
        )


def _display_repo_summary(results: list[InstallResult], dry_run: bool) -> None:
    """Display a summary of results for a single repository.

    Args:
        results: List of InstallResult objects for this repository
        dry_run: Whether this is a dry run
    """
    categorized = _categorize_results(results)
    component_type, component_type_singular = _get_component_type(results)

    # Log detailed file paths to the logger instead of printing them
    for result in results:
        if result.is_success and hasattr(result, "message"):
            if "saved to" in result.message:
                echo(
                    f"  {result.component_name}: {result.message}",
                    persona=Persona.POWER_USER,
                )
        elif result.status == InstallStatus.ALREADY_INSTALLED and hasattr(
            result, "message"
        ):
            echo(
                f"  {result.component_name}: {result.message}",
                persona=Persona.POWER_USER,
            )

    # Display concise summary
    if dry_run:
        if categorized["success"]:
            success_names = [r.component_name for r in categorized["success"]]
            _display_status_line(
                "→",
                "cyan",
                len(categorized["success"]),
                component_type,
                component_type_singular,
                "Would configure",
                success_names,
            )

        if categorized["already"]:
            _display_status_line(
                "✓",
                "green",
                len(categorized["already"]),
                component_type,
                component_type_singular,
                "already configured",
            )

        if categorized["failed"]:
            _display_status_line(
                "✗",
                "red",
                len(categorized["failed"]),
                component_type,
                component_type_singular,
                "would fail",
            )
            _display_failures(categorized["failed"])
    else:
        # Only show lines for what actually happened
        if categorized["success"]:
            success_names = [r.component_name for r in categorized["success"]]
            _display_status_line(
                "✓",
                "green",
                len(categorized["success"]),
                component_type,
                component_type_singular,
                "Configured",
                success_names,
            )

        if categorized["already"]:
            _display_status_line(
                "✓",
                "green",
                len(categorized["already"]),
                component_type,
                component_type_singular,
                "already configured",
            )

        if categorized["failed"]:
            _display_status_line(
                "✗",
                "red",
                len(categorized["failed"]),
                component_type,
                component_type_singular,
                "failed",
            )
            _display_failures(categorized["failed"])


def _display_repository_result(result: InstallResult, dry_run: bool) -> None:
    """Display the result of an operation for a single repository.

    Args:
        result: The operation result
        dry_run: Whether this is a dry run
    """
    # This function is now deprecated in favor of _display_repo_summary
    # But kept for backward compatibility with execute_in_git_repositories
    if dry_run:
        if result.is_success:
            echo(f"  Would install {result.component_name}", persona=Persona.POWER_USER)
        elif result.is_error:
            echo(
                f"  {click.style('✗', fg='red')} Would fail: {result.component_name}: {result.message}"
            )
        elif result.status == InstallStatus.ALREADY_INSTALLED:
            echo(
                f"  Already installed: {result.component_name}",
                persona=Persona.POWER_USER,
            )
    else:
        if result.is_success:
            echo(
                f"  {result.component_name}: {result.message}",
                persona=Persona.POWER_USER,
            )
        elif result.is_error:
            echo(
                f"  {click.style('✗', fg='red')} {result.component_name}: {result.message}"
            )
        elif result.status == InstallStatus.ALREADY_INSTALLED:
            echo(
                f"  {result.component_name}: {result.message}",
                persona=Persona.POWER_USER,
            )


def display_aggregated_results(
    mcp_results: list[tuple[Path, InstallResult]] = None,
    hook_results: list[tuple[Path, InstallResult]] = None,
    dry_run: bool = False,
) -> None:
    """Display aggregated results from multiple operations.

    This function combines results from MCP installations and hook installations
    into a single, unified display.

    Args:
        mcp_results: Results from MCP installations
        hook_results: Results from hook installations
        dry_run: Whether this is a dry run
    """
    all_results = []

    # Combine all results
    if mcp_results:
        all_results.extend(mcp_results)
    if hook_results:
        all_results.extend(hook_results)

    if not all_results:
        return

    # Group results by repository
    results_by_repo = {}
    for path, result in all_results:
        repo_name = path.name
        if repo_name not in results_by_repo:
            results_by_repo[repo_name] = {"path": path, "mcp": [], "hooks": []}

        # Categorize by type (hook vs MCP)
        if "hook" in result.component_name.lower():
            results_by_repo[repo_name]["hooks"].append(result)
        else:
            results_by_repo[repo_name]["mcp"].append(result)

    # Display results for each repository
    for repo_name, repo_data in sorted(results_by_repo.items()):
        echo(f"\n{click.style('Repository:', fg='cyan', bold=True)} {repo_name}")

        # Display MCP results
        if repo_data["mcp"]:
            _display_repo_summary(repo_data["mcp"], dry_run)

        # Display hook results
        if repo_data["hooks"]:
            _display_repo_summary(repo_data["hooks"], dry_run)

    # Display overall summary
    _display_overall_summary(all_results, dry_run)


def _display_overall_summary(
    all_results: list[tuple[Path, InstallResult]], dry_run: bool
) -> None:
    """Display the overall summary of operations across all repositories.

    Args:
        all_results: List of tuples of (repo_path, InstallResult)
        dry_run: Whether this is a dry run
    """
    echo(f"\n{click.style('Overall Summary:', fg='cyan', bold=True)}")

    # Analyze results to determine what was configured
    summary = _analyze_results_for_summary(all_results)

    # Determine component description
    component_desc = _get_component_description(
        summary["has_mcp"], summary["has_hooks"]
    )

    # Display summary based on dry_run mode
    if dry_run:
        _display_dry_run_summary(summary, component_desc)
    else:
        _display_execution_summary(summary, component_desc)


def _analyze_results_for_summary(all_results: list[tuple[Path, InstallResult]]) -> dict:
    """Analyze results to extract summary information.

    Returns:
        Dictionary containing summary statistics
    """
    summary = {
        "has_mcp": False,
        "has_hooks": False,
        "repos_with_success": set(),
        "repos_with_failures": set(),
        "repos_already_configured": set(),
        "failed_details": [],
    }

    for repo, result in all_results:
        # Determine component types
        if "hook" in result.component_name.lower():
            summary["has_hooks"] = True
        else:
            summary["has_mcp"] = True

        # Track repository status
        if result.is_success and result.status != InstallStatus.ALREADY_INSTALLED:
            summary["repos_with_success"].add(repo)
        elif result.status == InstallStatus.ALREADY_INSTALLED:
            summary["repos_already_configured"].add(repo)
        elif result.is_error:
            summary["repos_with_failures"].add(repo)
            summary["failed_details"].append((repo, result))

    return summary


def _get_component_description(has_mcp: bool, has_hooks: bool) -> str:
    """Get a description of what components were configured."""
    if has_mcp and has_hooks:
        return "the Zenable MCP server and hooks"
    elif has_mcp:
        return "the Zenable MCP server"
    elif has_hooks:
        return "hooks"
    else:
        return "components"


def _display_dry_run_summary(summary: dict, component_desc: str) -> None:
    """Display summary for dry-run mode."""
    repos_with_success = summary["repos_with_success"]
    repos_already_configured = summary["repos_already_configured"]
    repos_with_failures = summary["repos_with_failures"]

    if repos_with_success:
        count = len(repos_with_success)
        repo_text = f"repositor{'ies' if count != 1 else 'y'}"
        echo(
            f"  {click.style('→', fg='cyan')} Would configure {component_desc} in {count} {repo_text}"
        )

    if repos_already_configured and not repos_with_success:
        count = len(repos_already_configured)
        repo_text = f"repositor{'ies' if count != 1 else 'y'}"
        echo(
            f"  {click.style('✓', fg='green')} {component_desc.capitalize()} already configured in {count} {repo_text}"
        )

    if repos_with_failures:
        _display_failure_summary(
            repos_with_failures, summary["failed_details"], "would have"
        )


def _display_execution_summary(summary: dict, component_desc: str) -> None:
    """Display summary for actual execution mode."""
    repos_with_success = summary["repos_with_success"]
    repos_already_configured = summary["repos_already_configured"]
    repos_with_failures = summary["repos_with_failures"]

    if repos_with_success:
        count = len(repos_with_success)
        repo_text = f"repositor{'ies' if count != 1 else 'y'}"
        echo(
            f"  {click.style('✓', fg='green')} Successfully configured {component_desc} in {count} {repo_text}"
        )

    if repos_already_configured and not repos_with_success:
        count = len(repos_already_configured)
        repo_text = f"repositor{'ies' if count != 1 else 'y'}"
        echo(
            f"  {click.style('✓', fg='green')} {component_desc.capitalize()} already configured in {count} {repo_text}"
        )

    if repos_with_failures:
        _display_failure_summary(repos_with_failures, summary["failed_details"], "had")


def _display_failure_summary(
    repos_with_failures: set[Path],
    failed_details: list[tuple[Path, InstallResult]],
    verb: str,
    max_repos: int = 5,
) -> None:
    """Display a summary of failures.

    Args:
        repos_with_failures: Set of repositories that had failures
        failed_details: List of (repo, result) tuples for failures
        verb: Verb to use ("had" or "would have")
        max_repos: Maximum number of repositories to show details for
    """
    count = len(repos_with_failures)
    repo_text = f"repositor{'ies' if count != 1 else 'y'}"

    echo(f"  {click.style('✗', fg='red')} {count} {repo_text} {verb} failures")

    # Group failures by repository
    failures_by_repo = {}
    for repo, result in failed_details:
        if repo not in failures_by_repo:
            failures_by_repo[repo] = []
        failures_by_repo[repo].append(result.component_name)

    # Display details for up to max_repos repositories
    displayed = 0
    for repo, components in list(failures_by_repo.items())[:max_repos]:
        unique_components = list(set(components))
        echo(f"    - {repo.name}: {', '.join(unique_components)}")
        displayed += 1

    if len(failures_by_repo) > max_repos:
        remaining = len(failures_by_repo) - max_repos
        echo(
            f"    ...and {remaining} additional repositor{'ies' if remaining != 1 else 'y'}"
        )
