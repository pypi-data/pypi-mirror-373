import logging
from pathlib import Path
from typing import Protocol, Union

from pydantic import BaseModel, ConfigDict

LOG = logging.getLogger(__name__)


class FileProviderException(Exception):
    """Exception raised when a file provider fails."""


class ProviderFileNotFoundError(FileProviderException):
    """Exception raised when a file is not found."""


class ProviderMultipleFilesFoundError(FileProviderException):
    """Exception raised when multiple files are found."""

    def __init__(self, message: str, found_files: list[str]):
        super().__init__(message)
        self.found_files = found_files


class File(BaseModel):
    """Represents a file with path and content"""

    model_config = ConfigDict(strict=False)

    path: str
    content: str


class FileProvider(Protocol):
    def find_and_get_one_file(self, file_names: list[str]) -> File:
        """
        Returns the content of the file found in the provider that matches any of the file_names
        in any directory of the provider.
        Raises an exception if zero or more than one file is found.
        """

    def find_files(self, file_names: list[str]) -> list[Union[str, Path]]:
        """
        Search the provider for all files named file_names.
        file_names is a list of strings, so it can search for multiple files.
        It will search on any directory of the provider.
        Returns a list of file paths (relative to provider root).
        """

    def get_file(self, file_path: Union[str, Path]) -> File:
        """
        Fetch the content of the given file from the provider.
        """
