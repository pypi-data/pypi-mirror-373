"""Utilities for installation reporting and filtering."""

from pathlib import Path
from typing import Optional

import click
from pydantic import BaseModel, ConfigDict, ValidationError

from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.utils.files import filter_files_by_patterns


class FilterResult(BaseModel):
    """Result of filtering git repositories."""

    model_config = ConfigDict(strict=True, arbitrary_types_allowed=True)

    filtered_repos: list[Path]
    original_count: int
    filtered_count: int


def filter_git_repositories(
    git_repos: list[Path],
    include_patterns: Optional[list[str]] = None,
    exclude_patterns: Optional[list[str]] = None,
    handler_name: str = "recursive install",
) -> FilterResult:
    """
    Filter git repositories based on include/exclude patterns.

    Args:
        git_repos: List of git repository paths
        include_patterns: Optional list of glob patterns to include
        exclude_patterns: Optional list of glob patterns to exclude
        handler_name: Name for logging purposes

    Returns:
        FilterResult containing filtered_repos, original_count, and filtered_count
    """
    if not (include_patterns or exclude_patterns):
        try:
            return FilterResult(
                filtered_repos=git_repos,
                original_count=len(git_repos),
                filtered_count=0,
            )
        except ValidationError as e:
            echo(f"Error creating filter result: {e}", err=True)
            raise

    original_count = len(git_repos)
    filtered_repos = filter_files_by_patterns(
        git_repos,
        patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        handler_name=handler_name,
        directory_only=True,
    )
    filtered_count = original_count - len(filtered_repos)

    try:
        return FilterResult(
            filtered_repos=filtered_repos,
            original_count=original_count,
            filtered_count=filtered_count,
        )
    except ValidationError as e:
        echo(f"Error creating filter result: {e}", err=True)
        raise


def show_filtering_report(
    original_count: int,
    filtered_count: int,
    remaining_count: int,
    include_patterns: Optional[list[str]] = None,
    exclude_patterns: Optional[list[str]] = None,
    entity_name: str = "repository",
    entity_plural: str = "repositories",
) -> None:
    """
    Display a filtering report showing what was filtered and why.

    Args:
        original_count: Original number of entities
        filtered_count: Number of entities filtered out
        remaining_count: Number of entities remaining
        include_patterns: Include patterns used
        exclude_patterns: Exclude patterns used
        entity_name: Singular name of entity (e.g., "repository")
        entity_plural: Plural name of entity (e.g., "repositories")
    """
    if filtered_count == 0:
        return

    # Determine singular or plural for original count
    orig_text = entity_name if original_count == 1 else entity_plural
    filtered_text = entity_name if filtered_count == 1 else entity_plural

    if remaining_count == 0:
        # All entities were filtered out
        if include_patterns and exclude_patterns:
            echo(
                f"Found {original_count} git {orig_text}, but all were filtered out "
                f"based on the provided include/exclude patterns",
                log=False,
            )
        elif include_patterns:
            echo(
                f"Found {original_count} git {orig_text}, but all were filtered out - "
                f"none matched the include pattern(s): {', '.join(include_patterns)}",
                log=False,
            )
        elif exclude_patterns:
            echo(
                f"Found {original_count} git {orig_text}, but all were filtered out "
                f"by the exclude pattern(s): {', '.join(exclude_patterns)}",
                log=False,
            )
    else:
        # Some entities were filtered
        echo(f"\nFound {original_count} git {orig_text}", log=False)
        echo(
            f"Filtered out {filtered_count} {filtered_text} based on patterns",
            log=False,
        )


def show_repositories_to_configure(
    git_repos: list[Path],
    max_display: int = 10,
) -> None:
    """
    Display the list of repositories that will be configured.

    Args:
        git_repos: List of git repository paths
        max_display: Maximum number of repositories to display
    """
    if not git_repos:
        return

    # Sort repositories by name for consistent display order
    sorted_repos = sorted(git_repos, key=lambda p: p.name)

    echo("\nRepositories to be configured:", log=False)
    for repo in sorted_repos[:max_display]:
        repo_name = repo.name
        echo(f"  • {repo_name}", log=False)

    if len(sorted_repos) > max_display:
        echo(f"  ... and {len(sorted_repos) - max_display} more", log=False)


def show_filtering_results(
    original_count: int,
    include_patterns: Optional[list[str]] = None,
    exclude_patterns: Optional[list[str]] = None,
    entity_name: str = "repository",
    entity_plural: str = "repositories",
) -> None:
    """
    Show filtering results when all entities were filtered out by patterns.

    Args:
        original_count: Original number of entities before filtering
        include_patterns: Include patterns used
        exclude_patterns: Exclude patterns used
        entity_name: Singular name of entity (e.g., "repository")
        entity_plural: Plural name of entity (e.g., "repositories")
    """
    entity_text = entity_name if original_count == 1 else entity_plural
    if include_patterns and exclude_patterns:
        echo(
            f"Found {original_count} git {entity_text}, but all were filtered out "
            f"based on the provided include/exclude patterns",
            log=False,
        )
    elif include_patterns:
        echo(
            f"Found {original_count} git {entity_text}, but all were filtered out - "
            f"none matched the include pattern(s): {', '.join(include_patterns)}",
            log=False,
        )
    elif exclude_patterns:
        echo(
            f"Found {original_count} git {entity_text}, but all were filtered out "
            f"by the exclude pattern(s): {', '.join(exclude_patterns)}",
            log=False,
        )


def show_complete_filtering_information(
    git_repos: list[Path],
    original_count: int,
    was_filtered: bool,
    include_patterns: Optional[list[str]] = None,
    exclude_patterns: Optional[list[str]] = None,
    dry_run: bool = False,
    ask_confirmation: bool = True,
) -> bool:
    """
    Show complete filtering information including what was filtered and what will be configured.

    Args:
        git_repos: List of git repository paths after filtering
        original_count: Original number of repositories before filtering
        was_filtered: Whether filtering was applied
        include_patterns: Include patterns used
        exclude_patterns: Exclude patterns used
        dry_run: Whether this is a dry run
        ask_confirmation: Whether to ask for user confirmation

    Returns:
        True if user confirmed or confirmation not needed, False if user cancelled
    """
    if was_filtered and original_count != len(git_repos):
        filtered_count = original_count - len(git_repos)
        show_filtering_report(
            original_count,
            filtered_count,
            len(git_repos),
            include_patterns,
            exclude_patterns,
        )
    else:
        repo_text = "repository" if len(git_repos) == 1 else "repositories"
        echo(f"\nFound {len(git_repos)} git {repo_text}", log=False)

    # Show repositories to be configured
    show_repositories_to_configure(git_repos)

    # Ask for confirmation unless dry-run
    if ask_confirmation and not dry_run and git_repos:
        echo("", log=False)
        if not click.confirm(
            click.style("Do you want to proceed with the installation?", fg="yellow"),
            default=True,
        ):
            echo("Installation cancelled.")
            return False

    return True
