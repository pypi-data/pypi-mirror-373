"""
IDE context detection and file path extraction strategies.
"""

import json
import sys
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from pydantic import ValidationError

from zenable_mcp.file_discovery import get_most_recently_edited_file_with_filtering
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona
from zenable_mcp.models.claude_hook_input import ClaudeCodeHookInput


class IDEType(Enum):
    """Supported IDE types."""

    CLAUDE = "claude"
    KIRO = "kiro"
    CURSOR = "cursor"
    VSCODE = "vscode"
    WINDSURF = "windsurf"
    UNKNOWN = "unknown"


class IDEContextStrategy(ABC):
    """Abstract base class for IDE context strategies."""

    @abstractmethod
    def detect(self) -> bool:
        """Detect if this IDE context is active."""
        pass

    @abstractmethod
    def get_file_paths(self) -> Optional[list[str]]:
        """Extract file paths from the IDE context."""
        pass

    @abstractmethod
    def get_ide_type(self) -> IDEType:
        """Return the IDE type."""
        pass


class ClaudeContextStrategy(IDEContextStrategy):
    """Strategy for Claude Code IDE context."""

    def __init__(self):
        self._stdin_data: Optional[dict] = None
        self._stdin_read: bool = False
        self._validated_input: Optional[ClaudeCodeHookInput] = None

    def detect(self) -> bool:
        """Detect Claude Code context by validating JSON from stdin.

        Claude Code sends hook data as JSON to stdin. We detect it by:
        1. Checking if stdin is not a TTY (piped input)
        2. Attempting to parse JSON from stdin
        3. Validating the JSON matches the ClaudeCodeHookInput Pydantic model
        """
        stdin_data = self._read_stdin()
        if not stdin_data:
            return False

        # Use Pydantic model to validate the JSON structure
        try:
            self._validated_input = ClaudeCodeHookInput(**stdin_data)
            if self._validated_input.is_valid_claude_hook():
                echo(
                    "Claude Code context detected via Pydantic validation",
                    persona=Persona.DEVELOPER,
                )
                echo(
                    f"Tool name: {self._validated_input.tool_name}",
                    persona=Persona.DEVELOPER,
                )
                return True
        except ValidationError as e:
            echo(
                f"JSON does not match Claude Code hook structure: {e}",
                persona=Persona.DEVELOPER,
            )

        return False

    def _read_stdin(self) -> Optional[dict]:
        """Read and parse JSON from stdin if available.

        Returns:
            Parsed JSON data or None if stdin is a TTY or can't be parsed
        """
        if self._stdin_read:
            return self._stdin_data

        self._stdin_read = True

        # Check if stdin is a TTY (interactive terminal)
        # If it is, there's no piped input to read
        if sys.stdin.isatty():
            echo("stdin is a TTY, not reading input", persona=Persona.DEVELOPER)
            return None

        try:
            # Read stdin with 10MB size limit to prevent DoS attacks
            MAX_STDIN_SIZE = 10 * 1024 * 1024  # 10MB
            stdin_content = sys.stdin.read(MAX_STDIN_SIZE)

            # Check if we potentially hit the size limit
            if len(stdin_content) == MAX_STDIN_SIZE:
                # Try to read one more byte to see if there's more data
                if sys.stdin.read(1):
                    echo(
                        f"stdin input exceeds {MAX_STDIN_SIZE} bytes (10MB limit), truncating",
                        persona=Persona.POWER_USER,
                        err=True,
                    )

            # Parse the content as JSON
            self._stdin_data = json.loads(stdin_content)
            if isinstance(self._stdin_data, dict):
                return self._stdin_data
        except (json.JSONDecodeError, IOError, OSError) as e:
            echo(
                f"Failed to parse stdin as JSON (may exceed 10MB limit): {e}",
                persona=Persona.DEVELOPER,
            )
            self._stdin_data = None

        return None

    def get_file_paths(self) -> Optional[list[str]]:
        """
        Extract file paths from Claude context.

        Falls back to most recently edited git file.
        """
        file_paths = []

        # Use most recently edited file
        recent_file = get_most_recently_edited_file_with_filtering()
        if recent_file:
            file_paths.append(recent_file)
            msg = f"Using most recently edited file: {recent_file}"
            echo(msg, persona=Persona.POWER_USER)

        return file_paths if file_paths else None

    def get_ide_type(self) -> IDEType:
        """Return Claude IDE type."""
        return IDEType.CLAUDE


class KiroContextStrategy(IDEContextStrategy):
    """Strategy for Kiro IDE context."""

    def __init__(self):
        pass

    def detect(self) -> bool:
        """Detect Kiro IDE context."""
        # No specific env vars for auto-detection
        return False

    def get_file_paths(self) -> Optional[list[str]]:
        """Get file paths for Kiro - uses most recently edited file."""
        recent_file = get_most_recently_edited_file_with_filtering()
        if recent_file:
            msg = f"Kiro: Using most recently edited file: {recent_file}"
            echo(msg, persona=Persona.POWER_USER)
            return [recent_file]
        return None

    def get_ide_type(self) -> IDEType:
        """Return Kiro IDE type."""
        return IDEType.KIRO


class CursorContextStrategy(IDEContextStrategy):
    """Strategy for Cursor IDE context."""

    def __init__(self):
        pass

    def detect(self) -> bool:
        """Detect Cursor IDE context."""
        # No specific env vars for auto-detection
        return False

    def get_file_paths(self) -> Optional[list[str]]:
        """Get file paths for Cursor."""
        msg = "Cursor: Using most recently edited file"
        echo(msg, persona=Persona.POWER_USER)
        recent_file = get_most_recently_edited_file_with_filtering()
        if recent_file:
            return [recent_file]
        return None

    def get_ide_type(self) -> IDEType:
        """Return Cursor IDE type."""
        return IDEType.CURSOR


class VSCodeContextStrategy(IDEContextStrategy):
    """Strategy for VSCode IDE context."""

    def __init__(self):
        pass

    def detect(self) -> bool:
        """Detect VSCode IDE context."""
        # No specific env vars for auto-detection
        return False

    def get_file_paths(self) -> Optional[list[str]]:
        """Get file paths for VSCode."""
        msg = "VSCode: Using most recently edited file"
        echo(msg, persona=Persona.POWER_USER)
        recent_file = get_most_recently_edited_file_with_filtering()
        if recent_file:
            return [recent_file]
        return None

    def get_ide_type(self) -> IDEType:
        """Return VSCode IDE type."""
        return IDEType.VSCODE


class WindsurfContextStrategy(IDEContextStrategy):
    """Strategy for Windsurf IDE context."""

    def __init__(self):
        pass

    def detect(self) -> bool:
        """Detect Windsurf IDE context."""
        # No specific env vars for auto-detection
        return False

    def get_file_paths(self) -> Optional[list[str]]:
        """Get file paths for Windsurf."""
        msg = "Windsurf: Using most recently edited file"
        echo(msg, persona=Persona.POWER_USER)
        recent_file = get_most_recently_edited_file_with_filtering()
        if recent_file:
            return [recent_file]
        return None

    def get_ide_type(self) -> IDEType:
        """Return Windsurf IDE type."""
        return IDEType.WINDSURF


class IDEContextDetector:
    """
    Detects IDE context and extracts file paths using appropriate strategy.
    """

    def __init__(self) -> None:
        """Initialize with all available strategies."""
        self.strategies: list[IDEContextStrategy] = [
            ClaudeContextStrategy(),
            CursorContextStrategy(),
            VSCodeContextStrategy(),
            WindsurfContextStrategy(),
            KiroContextStrategy(),
        ]
        self._detected_strategy: Optional[IDEContextStrategy] = None

    def detect_context(self) -> IDEType:
        """
        Detect the current IDE context.

        Returns:
            IDEType: The detected IDE type, or UNKNOWN if none detected
        """
        for strategy in self.strategies:
            if strategy.detect():
                self._detected_strategy = strategy
                ide_type = strategy.get_ide_type()
                echo(
                    f"Detected {ide_type.value} IDE context", persona=Persona.POWER_USER
                )
                return ide_type

        return IDEType.UNKNOWN

    def get_file_paths(self) -> Optional[list[str]]:
        """
        Get file paths from the detected IDE context.

        Returns:
            List of file paths if available, None otherwise
        """
        if self._detected_strategy:
            paths = self._detected_strategy.get_file_paths()
            if paths:
                msg = f"Extracted {len(paths)} file path(s) from {self._detected_strategy.get_ide_type().value} context"
                echo(msg, persona=Persona.POWER_USER)
            return paths

        # Try each strategy if no context was previously detected
        for strategy in self.strategies:
            if strategy.detect():
                paths = strategy.get_file_paths()
                if paths:
                    msg = f"Extracted {len(paths)} file path(s) from {strategy.get_ide_type().value} context"
                    echo(msg, persona=Persona.POWER_USER)
                    return paths

        # If no IDE context was detected, fall back to most recently edited file
        echo(
            "No IDE context detected, attempting to find most recently edited file",
            persona=Persona.POWER_USER,
        )

        recent_file = get_most_recently_edited_file_with_filtering()
        if recent_file:
            return [recent_file]

        return None

    def get_detected_ide(self) -> IDEType:
        """
        Get the detected IDE type.

        Returns:
            IDEType: The detected IDE type, or UNKNOWN if none detected
        """
        if self._detected_strategy:
            return self._detected_strategy.get_ide_type()

        # Re-detect if needed
        return self.detect_context()


def get_files_from_environment() -> Optional[list[str]]:
    """
    Convenience function to get file paths from the current IDE context.

    Returns:
        List of file paths if available, None otherwise
    """
    detector = IDEContextDetector()
    detector.detect_context()
    return detector.get_file_paths()
