"""Custom exceptions for zenable_mcp."""

from typing import Optional

from zenable_mcp.exit_codes import ExitCode


class ZenableMCPError(Exception):
    """Base exception for all zenable_mcp errors.

    Attributes:
        exit_code: The exit code to use when this error causes program termination
        message: The error message
    """

    # Default to a general error code - subclasses should override with specific codes
    exit_code: ExitCode = ExitCode.INSTALLATION_ERROR

    def __init__(self, message: str, exit_code: Optional[ExitCode] = None):
        super().__init__(message)
        if exit_code is not None:
            self.exit_code = exit_code


class ConfigurationError(ZenableMCPError):
    """Raised when there are configuration issues."""

    exit_code = ExitCode.MISSING_API_KEY


class HandlerConflictError(ZenableMCPError):
    """Raised when multiple input handlers claim they can handle the input.

    Attributes:
        conflicting_handlers: List of handler names that are in conflict
    """

    exit_code = ExitCode.HANDLER_CONFLICT

    def __init__(self, handlers: list[str]):
        self.conflicting_handlers = handlers
        handler_names = " or ".join(handlers)
        super().__init__(f"Unable to identify which handler to use: {handler_names}")


class HandlerEnvironmentError(ZenableMCPError):
    """Raised when a handler detects it's not in the appropriate environment.

    This is used when handlers like ClaudeCodeInputHandler
    detect they're not running in their expected environment.
    """

    def __init__(self, handler_name: str, reason: str):
        super().__init__(f"{handler_name}: {reason}")


class FileOperationError(ZenableMCPError):
    """Base class for file-related errors."""

    exit_code = ExitCode.FILE_READ_ERROR


class NoFilesSpecifiedError(FileOperationError):
    """Raised when no files are specified and none can be detected from context."""

    exit_code = ExitCode.NO_FILES_SPECIFIED

    def __init__(self):
        super().__init__("No files specified and none detected from context")


class NoFilesFoundError(FileOperationError):
    """Raised when no files are found matching the specified patterns."""

    exit_code = ExitCode.NO_FILES_FOUND

    def __init__(self, patterns: Optional[list[str]] = None):
        if patterns:
            message = f"No files found matching patterns: {', '.join(patterns)}"
        else:
            message = "No files found matching specified patterns"
        super().__init__(message)


class FileReadError(FileOperationError):
    """Raised when there's an error reading a file."""

    exit_code = ExitCode.FILE_READ_ERROR

    def __init__(self, file_path: str, reason: str):
        super().__init__(f"Error reading file {file_path}: {reason}")


class APIError(ZenableMCPError):
    """Raised when there's an error communicating with the Zenable MCP server."""

    exit_code = ExitCode.API_ERROR

    def __init__(self, message: str):
        super().__init__(f"API error: {message}")


class ConformanceError(ZenableMCPError):
    """Raised when conformance issues are found."""

    exit_code = ExitCode.CONFORMANCE_ISSUES_FOUND

    def __init__(self, issues_count: int):
        super().__init__(f"Found {issues_count} conformance issue(s)")


class ParserError(ZenableMCPError):
    """Raised when there's an error parsing a file or configuration."""

    def __init__(self, file_path: str, reason: str):
        super().__init__(f"Failed to parse {file_path}: {reason}")


class InstructionsFileNotFoundError(ConfigurationError):
    """Raised when instructions file is not configured for an IDE."""

    def __init__(self, ide_name: str):
        super().__init__(f"Instructions file not configured for {ide_name}")


class GitRepositoryNotFoundError(FileOperationError):
    """Raised when not in a git repository when one is expected."""

    def __init__(self):
        super().__init__("Not in a git repository")


class ConfigFileNotFoundError(ConfigurationError):
    """Raised when no configuration file can be found."""

    def __init__(self, searched_paths: Optional[list[str]] = None):
        if searched_paths:
            paths = ", ".join(str(p) for p in searched_paths)
            message = f"No configuration file found in: {paths}"
        else:
            message = "No configuration file found"
        super().__init__(message)


class IDEContextNotDetectedError(ZenableMCPError):
    """Raised when IDE context cannot be detected."""

    def __init__(self):
        super().__init__("Unable to detect IDE context or recent file information")


class StdinNotAvailableError(ZenableMCPError):
    """Raised when stdin is expected but not available."""

    def __init__(self):
        super().__init__("No input available from stdin")


class InvalidInputFormatError(ZenableMCPError):
    """Raised when input data doesn't match expected format."""

    def __init__(self, expected_format: str, reason: str):
        super().__init__(f"Invalid {expected_format} format: {reason}")


class IDECapabilityError(ZenableMCPError):
    """Base exception for IDE capability-related errors."""

    exit_code = ExitCode.INSTALLATION_ERROR

    def __init__(self, ide_name: str, message: str, suggestion: Optional[str] = None):
        self.ide_name = ide_name
        self.suggestion = suggestion
        full_message = message
        if suggestion:
            full_message = f"{message}\n{suggestion}"
        super().__init__(full_message)


class GlobalConfigNotSupportedError(IDECapabilityError):
    """Raised when an IDE doesn't support global configuration."""

    def __init__(self, ide_name: str, suggestion: Optional[str] = None):
        if not suggestion:
            suggestion = f"To configure {ide_name}, run without the --global flag."
        super().__init__(
            ide_name, f"{ide_name} does not support global configuration", suggestion
        )


class ProjectConfigNotSupportedError(IDECapabilityError):
    """Raised when an IDE doesn't support project-level configuration."""

    def __init__(self, ide_name: str, suggestion: Optional[str] = None):
        if not suggestion:
            suggestion = f"To configure {ide_name}, use the --global flag:\n  uvx zenable-mcp install mcp {ide_name.lower()} --global"
        super().__init__(
            ide_name,
            f"{ide_name} does not support project-level configuration",
            suggestion,
        )


class HooksNotSupportedError(IDECapabilityError):
    """Raised when an IDE doesn't support hooks."""

    def __init__(self, ide_name: str, suggestion: Optional[str] = None):
        if not suggestion:
            suggestion = f"{ide_name} does not support hooks. Consider using MCP configuration instead."
        super().__init__(ide_name, f"{ide_name} does not support hooks", suggestion)


class InstructionsPathNotSupportedError(IDECapabilityError):
    """Raised when an IDE doesn't support instructions in the requested mode."""

    def __init__(
        self, ide_name: str, is_global: bool, suggestion: Optional[str] = None
    ):
        mode = "global" if is_global else "project-level"
        if not suggestion:
            alternate_mode = "project-level" if is_global else "global"
            suggestion = (
                f"To configure {ide_name} with instructions, use {alternate_mode} mode."
            )
        super().__init__(
            ide_name,
            f"{ide_name} does not support instructions in {mode} mode",
            suggestion,
        )
