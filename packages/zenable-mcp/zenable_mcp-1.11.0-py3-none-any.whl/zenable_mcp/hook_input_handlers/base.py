"""Base classes and interfaces for hook input handlers."""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from zenable_mcp.exit_codes import ExitCode

logger = logging.getLogger(__name__)


class HookInputFormat(Enum):
    """Supported hook input formats."""

    CLAUDE_CODE_HOOK = "claude_code_hook"
    UNKNOWN = "unknown"


class HookInputContext(BaseModel):
    """Context information extracted from various input sources."""

    model_config = ConfigDict(strict=True)

    format: HookInputFormat
    raw_data: Optional[dict[str, Any]] = None
    files: list[Path] = Field(default_factory=list)
    environment: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InputHandler(ABC):
    """Abstract base class for input handlers.

    Each handler is responsible for:
    1. Detecting if it can handle the current input context
    2. Parsing and extracting relevant information
    3. Returning structured data for processing
    """

    @abstractmethod
    def can_handle(self) -> bool:
        """Check if this handler can process the current input.

        This method should check various sources (stdin, env vars, files, etc.)
        to determine if this handler is applicable.

        Returns:
            True if this handler can process the input, False otherwise
        """
        pass

    @abstractmethod
    def parse_input(self) -> HookInputContext:
        """Parse the input and extract relevant information.

        Returns:
            HookInputContext containing parsed data and metadata
        """
        pass

    @abstractmethod
    def get_files(self) -> list[Path]:
        """Extract file paths that should be checked.

        Returns:
            List of Path objects for files to check
        """
        pass

    @abstractmethod
    def build_response_to_hook_call(
        self, has_findings: bool, findings_text: str = ""
    ) -> Optional[str]:
        """Build the response to send back to the hook caller.

        This formats the response according to the hook's protocol requirements
        (e.g., JSON for Claude Code hooks).

        Args:
            has_findings: Whether conformance issues were found
            findings_text: Text describing the findings

        Returns:
            Formatted response string for the hook or None if no special format needed
        """
        pass

    def format_response_for_humans(
        self, has_findings: bool, findings_text: str = ""
    ) -> str:
        """Format the response for human-readable output.

        This provides a user-friendly representation of the findings
        suitable for terminal output or logs.

        Args:
            has_findings: Whether conformance issues were found
            findings_text: Text describing the findings

        Returns:
            Human-readable response string
        """
        if has_findings:
            return f"Conformance issues found:\n{findings_text}"
        return "No conformance issues found."

    def get_exit_code(self, has_findings: bool) -> int:
        """Get the appropriate exit code for this handler.

        Args:
            has_findings: Whether conformance issues were found

        Returns:
            Exit code to use (default is SUCCESS)
        """
        return ExitCode.SUCCESS  # Default: success

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this handler."""
        pass

    @property
    @abstractmethod
    def format(self) -> HookInputFormat:
        """Get the input format this handler processes."""
        pass

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self.name}, format={self.format.value})"
        )
