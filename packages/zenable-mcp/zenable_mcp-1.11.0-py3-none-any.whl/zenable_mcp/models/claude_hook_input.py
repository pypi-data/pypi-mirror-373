"""Pydantic models for Claude Code hook input validation."""

from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class HookToolInputBase(BaseModel):
    """Base model for hook tool input."""

    file_path: Optional[str] = Field(
        None, description="Path to the file being operated on"
    )

    model_config = ConfigDict(extra="allow", strict=False)  # Allow tool-specific fields


class WriteHookToolInput(HookToolInputBase):
    """Input for Write hook tool."""

    file_path: str = Field(..., description="Path to the file being written")
    content: str = Field(..., description="Content to write to the file")


class EditHookToolInput(HookToolInputBase):
    """Input for Edit hook tool."""

    file_path: str = Field(..., description="Path to the file being edited")
    old_string: str = Field(..., description="String to find and replace")
    new_string: str = Field(..., description="Replacement string")
    replace_all: bool = Field(
        default=False, description="Whether to replace all occurrences"
    )


class HookEditItem(BaseModel):
    """Single edit operation for MultiEdit hook."""

    model_config = ConfigDict(strict=False)

    old_string: str = Field(..., description="String to find and replace")
    new_string: str = Field(..., description="Replacement string")
    replace_all: Optional[bool] = Field(
        default=False, description="Whether to replace all occurrences"
    )


class MultiEditHookToolInput(HookToolInputBase):
    """Input for MultiEdit hook tool."""

    file_path: str = Field(..., description="Path to the file being edited")
    edits: list[HookEditItem] = Field(..., description="List of edit operations")


class PostToolUseHookResponse(BaseModel):
    """
    Response format for PostToolUse Claude Code hook execution.

    This model represents the JSON response that should be output to stderr
    when a PostToolUse hook is executed, to control Claude Code's behavior after
    the hook runs.

    PostToolUse Decision Control:
    - If 'decision' is set to "block", it automatically prompts Claude with the 'reason'
    - If 'decision' is undefined/None, no action is taken and 'reason' is ignored
    """

    decision: Optional[str] = Field(
        None,
        description='Decision control: "block" to block tool execution, None to continue normally',
    )
    reason: Optional[str] = Field(
        None, description="Explanation for the decision (used when decision='block')"
    )

    model_config = ConfigDict(
        strict=True,
        extra="forbid",  # Strict validation - no extra fields allowed
    )


class ClaudeCodeHookInput(BaseModel):
    """
    Model for validating Claude Code hook input JSON.

    This model validates the JSON structure sent by Claude Code to hooks.
    The presence of tool_name and tool_input fields with proper structure
    indicates this is a valid Claude Code hook invocation.
    """

    # Required fields for Claude Code hook detection
    tool_name: str = Field(..., description="Name of the tool that was used")
    tool_input: dict[str, Any] = Field(..., description="Input provided to the tool")

    # Optional fields that may be present
    session_id: Optional[str] = Field(None, description="Unique session identifier")
    transcript_path: Optional[str] = Field(
        None, description="Path to conversation transcript"
    )
    cwd: Optional[str] = Field(None, description="Current working directory")
    hook_event_name: Optional[str] = Field(
        None, description="Event that triggered the hook"
    )

    model_config = ConfigDict(
        extra="allow",  # Allow additional fields that Claude might add
        str_strip_whitespace=True,  # Strip whitespace from strings
        strict=False,
    )

    def is_valid_claude_hook(self) -> bool:
        """
        Check if this is a valid Claude Code hook input.

        Returns:
            True if the input has the required structure for a Claude Code hook
        """
        # Must have tool_name and tool_input
        if not self.tool_name or not isinstance(self.tool_input, dict):
            return False

        # tool_input must be a non-empty dict
        if not self.tool_input:
            return False

        return True

    def get_tool_specific_input(
        self,
    ) -> Optional[Union[WriteHookToolInput, EditHookToolInput, MultiEditHookToolInput]]:
        """
        Get the tool-specific input model based on tool_name.

        Returns:
            Parsed tool input or None if the tool is not recognized
        """
        if self.tool_name == "Write":
            try:
                return WriteHookToolInput(**self.tool_input)
            except (ValidationError, TypeError, ValueError):
                return None
        elif self.tool_name == "Edit":
            try:
                return EditHookToolInput(**self.tool_input)
            except (ValidationError, TypeError, ValueError):
                return None
        elif self.tool_name == "MultiEdit":
            try:
                return MultiEditHookToolInput(**self.tool_input)
            except (ValidationError, TypeError, ValueError):
                return None

        # For other tools, return the base model
        try:
            return HookToolInputBase(**self.tool_input)
        except (ValidationError, TypeError, ValueError):
            return None
