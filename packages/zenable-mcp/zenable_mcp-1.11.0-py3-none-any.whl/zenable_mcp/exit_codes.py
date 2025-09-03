"""Exit code definitions for zenable_mcp."""

from enum import IntEnum


class ExitCode(IntEnum):
    """Exit codes for zenable_mcp commands.

    These exit codes provide clear semantic meaning for different
    types of errors and outcomes that can occur during execution.
    """

    # Success codes
    SUCCESS = 0  # Command completed successfully

    # Input/hook related codes
    CONFORMANCE_ISSUES_FOUND = 2  # Conformance issues were detected
    HANDLER_CONFLICT = 3  # Multiple input handlers claiming they can handle
    NO_HOOK_INPUT = 4  # No hook input detected when running hook command

    # File and pattern errors
    MISSING_API_KEY = 11  # ZENABLE_API_KEY environment variable not set
    NO_FILES_SPECIFIED = 12  # No files specified and none detected from context
    NO_FILES_FOUND = 13  # No files found matching specified patterns
    FILE_READ_ERROR = 14  # Error reading one or more files
    INVALID_PARAMETERS = 15  # Invalid command line parameters or options
    FILE_WRITE_ERROR = 16  # Error writing one or more files

    # API and network errors
    API_ERROR = 20  # Error communicating with Zenable MCP server

    # Installation results
    INSTALLATION_ERROR = 51  # Installation failed or configuration error
    PARTIAL_SUCCESS = 52  # Some installations succeeded, some failed

    # User interaction
    USER_INTERRUPT = 130  # User interrupted the process (Ctrl+C)
