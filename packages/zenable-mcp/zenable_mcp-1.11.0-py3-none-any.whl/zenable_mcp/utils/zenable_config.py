"""
Zenable configuration utilities for filtering and processing files.
"""

import logging
from pathlib import Path
from typing import Optional

import git
from git import Repo

from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona
from zenable_mcp.user_config.config_handler_factory import get_local_config_handler
from zenable_mcp.utils.files import should_skip_file

log = logging.getLogger(__name__)


def filter_files_by_zenable_config(
    files: list[Path], git_root: Optional[Path] = None
) -> list[Path]:
    """
    Filter files based on zenable_config exclusions.

    Args:
        files: List of Path objects to filter
        git_root: Optional git repository root path for relative path calculation

    Returns:
        Filtered list of Path objects
    """
    try:
        config_handler = get_local_config_handler()
        config, error = config_handler.load_config()

        if error:
            echo(
                f"Error loading config: {error}, using defaults",
                persona=Persona.DEVELOPER,
            )

        skip_patterns = config.pr_reviews.skip_filenames

        # If git_root not provided, try to find it once
        if git_root is None and files:
            try:
                # Use the parent directory of the first file to find the repo
                repo = Repo(
                    files[0].parent if files[0].is_file() else files[0],
                    search_parent_directories=True,
                )
                git_root = Path(repo.working_tree_dir)
            except git.InvalidGitRepositoryError:
                pass

        # Filter out files that match skip patterns
        filtered_files = []
        for file_path in files:
            # Convert path to relative path string for pattern matching
            # Use path relative to git root if possible
            if git_root:
                try:
                    relative_path = str(file_path.relative_to(git_root))
                except ValueError:
                    # Path is not relative to git root, use full path
                    relative_path = str(file_path)
            else:
                relative_path = str(file_path)

            if not should_skip_file(relative_path, skip_patterns):
                filtered_files.append(file_path)
            else:
                msg = f"Skipping file {relative_path} based on zenable_config patterns"
                echo(msg, persona=Persona.POWER_USER)

        return filtered_files
    except Exception as e:
        echo(
            f"Error filtering by zenable_config: {e}, returning all files",
            persona=Persona.DEVELOPER,
        )
        return files
