"""
Git utilities for finding modified files in the repository.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import git
from git import Repo

from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona

log = logging.getLogger(__name__)


def get_most_recently_edited_git_file(
    base_path: Optional[Path] = None,
) -> Optional[str]:
    """
    Find the most recently edited file that is also modified in the git working tree.

    This function finds files that are:
    1. Modified in the git working tree (either unstaged or staged, but not committed)
    2. Most recently modified based on filesystem timestamp
    3. Not ignored by .gitignore

    Args:
        base_path: The base directory to search from (defaults to current directory)

    Returns:
        Path to the most recently edited modified file, or None if no modified files
    """
    if base_path is None:
        base_path = Path.cwd()
    else:
        base_path = Path(base_path).resolve()

    try:
        # Find the git repository
        repo = Repo(base_path, search_parent_directories=True)
        git_root = Path(repo.working_tree_dir)

        echo(f"Git repository root: {git_root}", persona=Persona.POWER_USER)

        # Get list of modified files (both staged and unstaged)
        modified_files = []

        # Get unstaged changes
        unstaged_count = 0
        for item in repo.index.diff(None):  # diff against working tree
            file_path = git_root / item.a_path
            if file_path.exists() and file_path.is_file():
                modified_files.append(file_path)
                unstaged_count += 1
                echo(
                    f"  Found unstaged file: {item.a_path}", persona=Persona.POWER_USER
                )

        if unstaged_count > 0:
            echo(f"Found {unstaged_count} unstaged file(s)", persona=Persona.POWER_USER)

        # Get staged changes (only if there are commits in the repo)
        staged_count = 0
        if repo.head.is_valid():
            for item in repo.index.diff("HEAD"):  # diff against HEAD
                file_path = git_root / item.a_path
                if (
                    file_path.exists()
                    and file_path.is_file()
                    and file_path not in modified_files
                ):
                    modified_files.append(file_path)
                    staged_count += 1
                    echo(
                        f"  Found staged file: {item.a_path}",
                        persona=Persona.POWER_USER,
                    )
        else:
            # For repos with no commits, all staged files are new
            for (path, stage), entry in repo.index.entries.items():
                if stage == 0:  # Normal stage entry
                    file_path = git_root / path
                    if (
                        file_path.exists()
                        and file_path.is_file()
                        and file_path not in modified_files
                    ):
                        modified_files.append(file_path)
                        staged_count += 1
                        echo(
                            f"  Found staged file (no commits): {path}",
                            persona=Persona.POWER_USER,
                        )

        if staged_count > 0:
            echo(f"Found {staged_count} staged file(s)", persona=Persona.POWER_USER)

        # Get untracked files (repo.untracked_files already respects .gitignore)
        untracked_count = 0
        for file_path_str in repo.untracked_files:
            file_path = git_root / file_path_str
            if file_path.exists() and file_path.is_file():
                modified_files.append(file_path)
                untracked_count += 1
                echo(
                    f"  Found untracked file: {file_path_str}",
                    persona=Persona.POWER_USER,
                )

        if untracked_count > 0:
            echo(
                f"Found {untracked_count} untracked file(s)", persona=Persona.POWER_USER
            )

        echo(
            f"Total modified files found: {len(modified_files)}",
            persona=Persona.POWER_USER,
        )

        if not modified_files:
            msg = "No modified files found in git repository"
            echo(msg, persona=Persona.POWER_USER)
            return None

        # Find the most recently modified file based on filesystem timestamp
        echo(
            f"Checking modification times for {len(modified_files)} files...",
            persona=Persona.POWER_USER,
        )
        for f in modified_files:
            mtime = f.stat().st_mtime
            mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            echo(
                f"  {f.relative_to(git_root) if f.is_relative_to(git_root) else f}: {mtime_str}",
                persona=Persona.DEVELOPER,
            )

        most_recent_file = max(modified_files, key=lambda f: f.stat().st_mtime)

        msg = f"Selected most recently edited file: {most_recent_file}"
        echo(msg, persona=Persona.POWER_USER)
        return str(most_recent_file)

    except git.InvalidGitRepositoryError:
        echo(f"Not in a git repository: {base_path}", persona=Persona.DEVELOPER)
        return None
    except (OSError, IOError, AttributeError, TypeError, ValueError) as e:
        echo(f"Error finding most recently edited file: {e}", persona=Persona.DEVELOPER)
        return None


def get_git_modified_files(base_path: Optional[Path] = None) -> list[str]:
    """
    Get all files modified in the git working tree.

    This function finds files that are:
    1. Modified in the git working tree (either unstaged or staged, but not committed)
    2. Not ignored by .gitignore

    Args:
        base_path: The base directory to search from (defaults to current directory)

    Returns:
        List of paths to modified files
    """
    if base_path is None:
        base_path = Path.cwd()
    else:
        base_path = Path(base_path).resolve()

    try:
        # Find the git repository
        repo = Repo(base_path, search_parent_directories=True)
        git_root = Path(repo.working_tree_dir)

        modified_files = []

        # Get unstaged changes
        for item in repo.index.diff(None):  # diff against working tree
            file_path = git_root / item.a_path
            if file_path.exists() and file_path.is_file():
                modified_files.append(str(file_path))

        # Get staged changes (only if there are commits in the repo)
        if repo.head.is_valid():
            for item in repo.index.diff("HEAD"):  # diff against HEAD
                file_path = git_root / item.a_path
                if (
                    file_path.exists()
                    and file_path.is_file()
                    and str(file_path) not in modified_files
                ):
                    modified_files.append(str(file_path))
        else:
            # For repos with no commits, all staged files are new
            for (path, stage), entry in repo.index.entries.items():
                if stage == 0:  # Normal stage entry
                    file_path = git_root / path
                    if (
                        file_path.exists()
                        and file_path.is_file()
                        and str(file_path) not in modified_files
                    ):
                        modified_files.append(str(file_path))

        # Get untracked files (repo.untracked_files already respects .gitignore)
        for file_path_str in repo.untracked_files:
            file_path = git_root / file_path_str
            if file_path.exists() and file_path.is_file():
                modified_files.append(str(file_path))

        return modified_files

    except git.InvalidGitRepositoryError:
        return []
    except (OSError, IOError, AttributeError, TypeError, ValueError):
        return []


def get_branch_changed_files(
    base_path: Optional[Path] = None, base_branch: str = "main"
) -> list[Path]:
    """
    Get all files changed on the current branch compared to a base branch.

    This function finds files that are:
    1. Changed between the base branch and the current branch (committed changes)
    2. Modified in the working tree (staged and unstaged changes)
    3. Untracked files (not ignored by .gitignore)

    Args:
        base_path: The base directory to search from (defaults to current directory)
        base_branch: The base branch to compare against (default "main")

    Returns:
        List of Path objects for changed files
    """
    if base_path is None:
        base_path = Path.cwd()
    else:
        base_path = Path(base_path).resolve()

    try:
        # Find the git repository
        repo = Repo(base_path, search_parent_directories=True)
        git_root = Path(repo.working_tree_dir)

        echo(f"Git repository root: {git_root}", persona=Persona.DEVELOPER)
        echo(
            f"Comparing current branch against base branch: {base_branch}",
            persona=Persona.POWER_USER,
        )

        changed_files = set()

        # Get the merge base between current branch and base branch
        try:
            # Get current branch name
            current_branch = repo.active_branch.name
            echo(f"Current branch: {current_branch}", persona=Persona.DEVELOPER)

            # Find merge base
            merge_base = repo.merge_base(base_branch, current_branch)
            if merge_base:
                merge_base_commit = merge_base[0]
                echo(
                    f"Found merge base: {merge_base_commit.hexsha[:8]}",
                    persona=Persona.DEVELOPER,
                )

                # Get all files changed between merge base and current HEAD
                diff = merge_base_commit.diff(repo.head.commit)
                for item in diff:
                    # GitPython diff change types:
                    # 'A' = Added, 'D' = Deleted, 'M' = Modified, 'R' = Renamed

                    if item.change_type == "D":
                        # Deleted file - add it even though it doesn't exist
                        file_path = git_root / item.a_path
                        changed_files.add(file_path)
                    elif item.change_type in ["A", "M"]:
                        # Added or modified file
                        file_path = git_root / item.b_path
                        if file_path.exists() and file_path.is_file():
                            changed_files.add(file_path)
                    elif item.change_type.startswith("R"):
                        # Renamed file (e.g., 'R100' for 100% similarity)
                        # Add the new path if it exists
                        if item.b_path:
                            new_path = git_root / item.b_path
                            if new_path.exists() and new_path.is_file():
                                changed_files.add(new_path)
                        # For renamed files, we might also want the old path if different
                        if item.a_path and item.a_path != item.b_path:
                            old_path = git_root / item.a_path
                            # Old path usually won't exist for renames, but add if it does
                            if old_path.exists() and old_path.is_file():
                                changed_files.add(old_path)
                    else:
                        # Handle any other change types generically
                        if item.b_path:
                            file_path = git_root / item.b_path
                            if file_path.exists() and file_path.is_file():
                                changed_files.add(file_path)
                        elif item.a_path:
                            file_path = git_root / item.a_path
                            if file_path.exists() and file_path.is_file():
                                changed_files.add(file_path)

                echo(
                    f"Found {len(changed_files)} file(s) changed in commits on current branch",
                    persona=Persona.POWER_USER,
                )
            else:
                echo(
                    f"Warning: Could not find merge base with {base_branch}",
                    persona=Persona.POWER_USER,
                    err=True,
                )
        except (git.GitCommandError, TypeError) as e:
            echo(
                f"Warning: Could not compare with {base_branch}: {e}",
                persona=Persona.POWER_USER,
                err=True,
            )

        # Also include uncommitted changes (staged, unstaged, and untracked)
        working_tree_changes = get_git_modified_files(base_path)
        initial_count = len(changed_files)
        # Convert string paths to Path objects
        changed_files.update(Path(f) for f in working_tree_changes)
        added_count = len(changed_files) - initial_count

        if added_count > 0:
            echo(
                f"Found {added_count} additional file(s) with uncommitted changes",
                persona=Persona.POWER_USER,
            )

        # Convert set to sorted list for consistent ordering
        result = sorted(list(changed_files))
        echo(
            f"Total files changed on branch: {len(result)}",
            persona=Persona.POWER_USER,
        )

        return result

    except git.InvalidGitRepositoryError:
        echo(
            f"Not in a git repository: {base_path}",
            err=True,
            persona=Persona.POWER_USER,
        )
        return []
    except (
        OSError,
        IOError,
        AttributeError,
        TypeError,
        ValueError,
        git.GitCommandError,
    ) as e:
        echo(
            f"Error finding branch changed files: {e}",
            persona=Persona.POWER_USER,
            err=True,
        )
        return []
