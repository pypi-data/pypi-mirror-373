"""Pydantic models for hook configuration validation - internal use only."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class _HookConfig(BaseModel):
    """Base model for hook configuration."""

    script: Optional[str] = Field(None, description="Script to execute")
    command: Optional[str] = Field(None, description="Command to execute")
    enabled: bool = Field(default=True, description="Whether the hook is enabled")

    model_config = ConfigDict(strict=False, extra="allow")  # Allow IDE-specific fields


class _ClaudeCodeHookConfig(BaseModel):
    """Claude Code specific hook configuration."""

    userPromptPostHook: Optional[str] = Field(
        None, description="Hook to run after user prompt"
    )

    model_config = ConfigDict(strict=False, extra="allow")


class _ClaudeCodeSettings(BaseModel):
    """Claude Code settings.json structure."""

    hooks: Optional[_ClaudeCodeHookConfig] = Field(
        None, description="Claude Code hooks configuration"
    )

    model_config = ConfigDict(strict=False, extra="allow")  # Allow other settings


class _ZenableHookConfig(BaseModel):
    """Zenable-specific hook configuration."""

    script: str = Field(..., description="The Zenable conformance check script")

    model_config = ConfigDict(strict=True, extra="forbid")

    @field_validator("script")
    def validate_script(cls, v):
        if "zenable conformance_check" not in v:
            raise ValueError("Hook script must include 'zenable conformance_check'")
        return v


def _validate_hook_config(
    existing_config: dict[str, Any], ide_name: str
) -> tuple[bool, Optional[str]]:
    """Validate hook configuration for an IDE.

    Args:
        existing_config: The existing configuration dictionary
        ide_name: Name of the IDE

    Returns:
        Tuple of (is_valid, error_message)
    """
    if ide_name.lower() == "claude-code":
        try:
            settings = _ClaudeCodeSettings.model_validate(existing_config)
            if settings.hooks and settings.hooks.userPromptPostHook:
                if "zenable conformance_check" in settings.hooks.userPromptPostHook:
                    return True, None
                else:
                    return (
                        False,
                        "Hook exists but doesn't include Zenable conformance check",
                    )
            return False, "No userPromptPostHook configured"
        except Exception as e:
            return False, f"Invalid configuration: {str(e)}"

    # For other IDEs, hooks might not be applicable
    return True, None
