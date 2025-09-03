"""Claude Code hook input handler."""

import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

from zenable_mcp.exceptions import HandlerEnvironmentError
from zenable_mcp.exit_codes import ExitCode
from zenable_mcp.hook_input_handlers.base import (
    HookInputContext,
    HookInputFormat,
    InputHandler,
)
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona
from zenable_mcp.models.claude_hook_input import PostToolUseHookResponse


class ClaudeCodeInputHandler(InputHandler):
    """Handler for Claude Code hook inputs.

    Claude Code sends hook data as JSON to stdin with the following schema:
    {
        "session_id": "abc123",                    # Unique session identifier
        "transcript_path": "/path/to/transcript.jsonl",  # Path to conversation transcript
        "cwd": "/working/directory",               # Current working directory
        "hook_event_name": "PostToolUse",         # Event that triggered the hook
        "tool_name": "Write",                      # Tool that was used (Write, Edit, MultiEdit, etc.)
        "tool_input": {                           # Input provided to the tool
            "file_path": "/path/to/file.txt",
            "content": "file content"              # For Write tool
            # OR for Edit/MultiEdit:
            # "old_string": "text to replace",
            # "new_string": "replacement text"
        },
        "tool_response": {                         # Response from the tool
            "filePath": "/path/to/file.txt",      # Note: camelCase in response
            "success": true                        # Whether the tool succeeded
        }
    }

    The tool_input field varies based on the tool_name:

    For "Write" tool:
        "tool_input": {
            "file_path": "/path/to/file.txt",
            "content": "entire file content"
        }

    For "Edit" tool:
        "tool_input": {
            "file_path": "/path/to/file.txt",
            "old_string": "text to find and replace",
            "new_string": "replacement text",
            "replace_all": false  # Optional, defaults to false
        }

    For "MultiEdit" tool:
        "tool_input": {
            "file_path": "/path/to/file.txt",
            "edits": [
                {
                    "old_string": "first text to replace",
                    "new_string": "first replacement"
                },
                {
                    "old_string": "second text to replace",
                    "new_string": "second replacement"
                }
            ]
        }
    """

    def __init__(self):
        self._stdin_data: Optional[dict[str, Any]] = None
        self._stdin_read: bool = False

    @property
    def name(self) -> str:
        return "ClaudeCode"

    @property
    def format(self) -> HookInputFormat:
        return HookInputFormat.CLAUDE_CODE_HOOK

    def can_handle(self) -> bool:
        """Check if we're running as a Claude Code hook.

        Checks for:
        1. Non-TTY stdin with JSON data
        2. JSON contains expected Claude Code fields
        3. Optional: CLAUDE_HOOK_EVENT_NAME environment variable
        """
        # Check environment variable hint (optional)
        if os.environ.get("CLAUDE_HOOK_EVENT_NAME"):
            echo(
                "Found CLAUDE_HOOK_EVENT_NAME environment variable",
                persona=Persona.DEVELOPER,
            )
            return True

        # Check stdin for Claude Code JSON
        stdin_data = self._read_stdin()
        if not stdin_data:
            return False

        # Check for Claude Code specific fields
        required_fields = {"tool_name", "tool_input"}
        has_required = all(field in stdin_data for field in required_fields)

        if has_required and isinstance(stdin_data.get("tool_input"), dict):
            echo("Detected Claude Code hook format in stdin", persona=Persona.DEVELOPER)
            return True

        return False

    def parse_input(self) -> HookInputContext:
        """Parse Claude Code hook input from stdin."""
        stdin_data = self._read_stdin()
        if not stdin_data:
            raise HandlerEnvironmentError(
                "ClaudeCode", "No Claude Code input available"
            )

        # Extract relevant information
        tool_name = stdin_data.get("tool_name", "")
        tool_input = stdin_data.get("tool_input", {})
        tool_response = stdin_data.get("tool_response", {})

        # Extract files based on tool type
        files = []
        file_content = None

        if tool_name in ["Write", "Edit", "MultiEdit"]:
            file_path_str = tool_input.get("file_path")
            if file_path_str:
                file_path = Path(file_path_str)
                files.append(file_path)

                # For Write tool, we have the content in the input
                if tool_name == "Write" and "content" in tool_input:
                    file_content = tool_input["content"]

        # Build context
        context = HookInputContext(
            format=self.format,
            raw_data=stdin_data,
            files=files,
            environment={
                "CLAUDE_HOOK_EVENT_NAME": stdin_data.get("hook_event_name", ""),
                "CLAUDE_SESSION_ID": stdin_data.get("session_id", ""),
                "CLAUDE_CWD": stdin_data.get("cwd", ""),
            },
            metadata={
                "tool_name": tool_name,
                "tool_input": tool_input,
                "tool_response": tool_response,
                "transcript_path": stdin_data.get("transcript_path"),
                "file_content": file_content,  # Only for Write tool
            },
        )

        return context

    def get_files(self) -> list[Path]:
        """Extract file paths from Claude Code input."""
        context = self.parse_input()
        return context.files

    def build_response_to_hook_call(
        self, has_findings: bool, findings_text: str = ""
    ) -> Optional[str]:
        """Build response as JSON for PostToolUse Claude Code hook.

        Uses the PostToolUse Decision Control format:
        - decision: "block" to block execution, None to continue
        - reason: Explanation shown to Claude when blocking

        When there are findings, we block execution and provide the
        findings as the reason, prompting Claude to address them.
        """
        if has_findings and findings_text:
            # Block execution and provide findings as the reason
            # This will automatically prompt Claude with the reason
            response = PostToolUseHookResponse(decision="block", reason=findings_text)
        else:
            # No findings, continue normally
            response = PostToolUseHookResponse(decision=None, reason=None)

        # Use Pydantic's model_dump with mode="json" for proper serialization
        # and exclude_none to omit null fields
        return json.dumps(response.model_dump(mode="json", exclude_none=True))

    def get_exit_code(self, has_findings: bool) -> int:
        """Get the appropriate exit code for Claude Code handler.

        Args:
            has_findings: Whether conformance issues were found

        Returns:
            CONFORMANCE_ISSUES_FOUND if there are findings (to instruct IDE), SUCCESS otherwise
        """
        return ExitCode.CONFORMANCE_ISSUES_FOUND if has_findings else ExitCode.SUCCESS

    def _read_stdin(self) -> Optional[dict[str, Any]]:
        """Read and parse JSON from stdin if available.

        Returns:
            Parsed JSON data or None if stdin is a tty or can't be read
        """
        if self._stdin_read:
            return self._stdin_data

        self._stdin_read = True

        if sys.stdin.isatty():
            echo(
                "Error: stdin is a tty, not reading input",
                persona=Persona.DEVELOPER,
                err=True,
            )
            return None

        try:
            # Try to parse as JSON
            self._stdin_data = json.load(sys.stdin)
            if isinstance(self._stdin_data, dict):
                return self._stdin_data
        except (json.JSONDecodeError, IOError, OSError) as e:
            echo(
                f"Error: Failed to parse stdin as JSON: {e}",
                persona=Persona.DEVELOPER,
                err=True,
            )
            self._stdin_data = None

        return None
