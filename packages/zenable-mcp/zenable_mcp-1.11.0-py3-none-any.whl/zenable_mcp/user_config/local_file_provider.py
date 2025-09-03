from pathlib import Path
from typing import Optional

import git

from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona
from zenable_mcp.user_config.file_provider import (
    File,
    FileProvider,
    ProviderFileNotFoundError,
    ProviderMultipleFilesFoundError,
)


def _find_git_root(current_dir: Path) -> Optional[Path]:
    """
    Find the root of the git repository if we're in one.

    Returns:
        Path to git root if in a git repo, None otherwise.
    """
    try:
        repo = git.Repo(current_dir, search_parent_directories=True)
        return Path(repo.working_dir)
    except (ImportError, git.InvalidGitRepositoryError, git.NoSuchPathError):
        echo(
            "Not in a git repository or gitpython not installed",
            persona=Persona.DEVELOPER,
            err=True,
        )
        return None


class LocalFileProvider(FileProvider):
    """
    File provider that searches for configuration files starting from the current
    directory and going up to the git repository root (if in a git repo).
    """

    def __init__(self, current_dir: Optional[str] = None):
        """
        Initialize the MCP file provider.

        Defines the root directory for file search:
        - If current_dir is in a git repo, it will search from git repo including every
            subdirectory.
        - If current_dir is not in a git repo, it will search from current directory only, no
            subfolders, so the search scope is more limited.

        Args:
            current_dir: Current directory for repo detection and file search. Defaults to current
              working directory.
        """
        current_dir_path = Path(current_dir) if current_dir else Path.cwd()
        git_root = _find_git_root(current_dir_path)
        if git_root is not None:
            self.start_dir = git_root
            self.__is_in_git_repo = True
        else:
            self.start_dir = current_dir_path
            self.__is_in_git_repo = False

    def find_and_get_one_file(self, file_names: list[str]) -> File:
        """
        Search for configuration files starting from the current directory and
        going up to the git root (if in a git repo).

        Args:
            file_names: List of file names to search for (e.g., ['zenable_config.toml', 'zenable_config.yaml'])

        Returns:
            File object if exactly one file is found.

        Raises:
            ProviderFileNotFoundError: If no matching files are found.
            ProviderMultipleFilesFoundError: If multiple matching files are found.
        """
        found_files = self.find_files(file_names)

        if len(found_files) == 0:
            raise ProviderFileNotFoundError(
                f"No file found that matches any of the file names: {file_names}"
            )

        if len(found_files) > 1:
            raise ProviderMultipleFilesFoundError(
                f"Multiple files found that match the file names {file_names}.",
                found_files=found_files,
            )

        file_path = found_files[0]
        return self.get_file(file_path)

    def find_files(self, file_names: list[str]) -> list[Path]:
        """
        Search for files with the given names starting from the current directory
        and going up to the git root (if in a git repo).

        Args:
            file_names: List of file names to search for.

        Returns:
            List of Path objects for found files.
        """
        current_dir = self.start_dir.resolve()

        found_files = []
        for file_name in file_names:
            # If we are in a git repo we need to find subfolders, if not we only search the current
            #   directory
            if self.__is_in_git_repo:
                found_files.extend(current_dir.rglob(file_name))
            else:
                found_files.extend(current_dir.glob(file_name))

        return found_files

    def get_file(self, file_path: Path) -> File:
        """
        Read the content of a file.

        Args:
            file_path: Path to the file to read.

        Returns:
            File object if it exists, otherwise raises an exception.
        """
        try:
            return File(
                path=str(file_path.resolve()),
                content=file_path.read_text(encoding="utf-8"),
            )
        except Exception:
            echo(
                f"Failed to read file {file_path}", persona=Persona.DEVELOPER, err=True
            )
            raise
