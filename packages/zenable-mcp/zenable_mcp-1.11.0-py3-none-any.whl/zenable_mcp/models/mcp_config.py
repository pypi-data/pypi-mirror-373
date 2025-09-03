"""Pydantic models for MCP configuration validation."""

import os
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Constants
ZENABLE_MCP_ENDPOINT = os.environ.get(
    "ZENABLE_API_ENDPOINT", "https://mcp.www.zenable.app/"
)


class _MCPServerConfig(BaseModel):
    """Base model for MCP server configuration."""

    command: str = Field(..., description="The command to execute")
    args: list[str] = Field(
        default_factory=list, description="Arguments for the command"
    )
    disabled: Optional[bool] = Field(None, description="Whether the server is disabled")
    alwaysAllow: Optional[list[str]] = Field(
        None, description="Tools to always allow without prompting"
    )
    autoApprove: Optional[list[str]] = Field(None, description="Tools to auto-approve")
    trust: Optional[bool] = Field(None, description="Whether to trust this server")

    model_config = ConfigDict(
        strict=False, extra="allow"
    )  # Allow additional fields for flexibility


class _ZenableMCPConfig(_MCPServerConfig):
    """Zenable-specific MCP server configuration."""

    command: str = Field(default="npx", description="The command to execute")
    args: list[str] = Field(
        ..., description="Arguments including mcp-remote and API key"
    )

    @field_validator("command")
    def validate_command(cls, v):
        if v != "npx":
            raise ValueError(f"Zenable MCP must use 'npx' command, got '{v}'")
        return v

    @field_validator("args")
    def validate_args(cls, v):
        if not v:
            raise ValueError("Args cannot be empty")

        # Check for required components
        args_str = " ".join(v)

        if "mcp-remote" not in args_str:
            raise ValueError("Args must include 'mcp-remote'")

        if ZENABLE_MCP_ENDPOINT not in args_str:
            raise ValueError(
                f"Args must include Zenable MCP endpoint: {ZENABLE_MCP_ENDPOINT}"
            )

        # Check for API key
        has_api_key = any("API_KEY:" in arg for arg in v)
        if not has_api_key:
            raise ValueError("Args must include API_KEY header")

        return v

    @model_validator(mode="after")
    def validate_mcp_remote_version(self):
        """Validate that mcp-remote uses @latest version."""
        for arg in self.args:
            if "mcp-remote@" in arg and "@latest" not in arg:
                raise ValueError(f"mcp-remote must use @latest version, got: {arg}")
        return self


class _RooMCPConfig(_ZenableMCPConfig):
    """Roo-specific MCP configuration with strict requirements."""

    disabled: bool = Field(default=False, description="Must be explicitly set to false")
    alwaysAllow: list[str] = Field(
        default_factory=lambda: ["conformance_check"],
        description="Must include conformance_check",
    )

    @field_validator("disabled")
    def validate_disabled(cls, v):
        if v is not False:
            raise ValueError(f"Roo MCP must have disabled=false, got {v}")
        return v

    @field_validator("alwaysAllow")
    def validate_always_allow(cls, v):
        if "conformance_check" not in v:
            raise ValueError("Roo MCP must have 'conformance_check' in alwaysAllow")
        return v


class _KiroMCPConfig(_ZenableMCPConfig):
    """Kiro-specific MCP configuration."""

    disabled: bool = Field(default=False, description="Must be explicitly set to false")
    autoApprove: list[str] = Field(
        default_factory=lambda: ["conformance_check"],
        description="Must include conformance_check",
    )

    @field_validator("disabled")
    def validate_disabled(cls, v):
        if v is not False:
            raise ValueError(f"Kiro MCP must have disabled=false, got {v}")
        return v

    @field_validator("autoApprove")
    def validate_auto_approve(cls, v):
        if "conformance_check" not in v:
            raise ValueError("Kiro MCP must have 'conformance_check' in autoApprove")
        return v


class _GeminiMCPConfig(_ZenableMCPConfig):
    """Gemini CLI-specific MCP configuration."""

    trust: bool = Field(default=True, description="Must be set to true")

    @field_validator("trust")
    def validate_trust(cls, v):
        if v is not True:
            raise ValueError(f"Gemini MCP must have trust=true, got {v}")
        return v


class _VSCodeMCPConfig(BaseModel):
    """VS Code-specific MCP server configuration."""

    type: Literal["sse"] = Field(default="sse", description="Server type")
    url: str = Field(..., description="URL for SSE server")
    headers: dict[str, str] = Field(
        ..., description="HTTP headers with API key variable"
    )

    model_config = ConfigDict(
        strict=False, extra="allow"
    )  # Allow additional fields for flexibility

    @field_validator("url")
    def validate_url(cls, v):
        if not v:
            raise ValueError("URL cannot be empty")
        if ZENABLE_MCP_ENDPOINT not in v:
            raise ValueError(
                f"URL must be Zenable MCP endpoint: {ZENABLE_MCP_ENDPOINT}, got '{v}'"
            )
        return v

    @field_validator("headers")
    def validate_headers(cls, v):
        if not v:
            raise ValueError("Headers cannot be empty")
        if "API_KEY" not in v:
            raise ValueError("Headers must include API_KEY")
        # VS Code uses variable substitution
        api_value = v.get("API_KEY", "")
        if not api_value or "${input:" not in api_value:
            raise ValueError(
                "API_KEY header must use VS Code variable substitution (${input:...})"
            )
        return v


class _ClaudeCodeMCPConfig(BaseModel):
    """Claude Code-specific MCP server configuration (current format)."""

    type: Literal["sse"] = Field(default="sse", description="Server type")
    url: str = Field(..., description="URL for SSE server")
    headers: dict[str, str] = Field(..., description="HTTP headers with API key")

    model_config = ConfigDict(
        strict=False, extra="allow"
    )  # Allow additional fields for flexibility

    @field_validator("url")
    def validate_url(cls, v):
        if not v:
            raise ValueError("URL cannot be empty")
        if ZENABLE_MCP_ENDPOINT not in v:
            raise ValueError(
                f"URL must be Zenable MCP endpoint: {ZENABLE_MCP_ENDPOINT}, got '{v}'"
            )
        return v

    @field_validator("headers")
    def validate_headers(cls, v):
        if not v:
            raise ValueError("Headers cannot be empty")
        if "API_KEY" not in v:
            raise ValueError("Headers must include API_KEY")
        if not v.get("API_KEY"):
            raise ValueError("API_KEY header cannot be empty")
        return v


class _AmazonQMCPConfig(BaseModel):
    """Amazon Q-specific MCP configuration."""

    url: str = Field(..., description="URL for the MCP server")
    disabled: bool = Field(default=False, description="Whether the server is disabled")
    timeout: int = Field(default=3000, description="Timeout in milliseconds")
    headers: dict[str, str] = Field(..., description="HTTP headers with API key")

    model_config = ConfigDict(
        strict=False, extra="allow"
    )  # Allow additional fields for flexibility

    @field_validator("url")
    def validate_url(cls, v):
        if not v:
            raise ValueError("URL cannot be empty")
        if ZENABLE_MCP_ENDPOINT not in v:
            raise ValueError(
                f"URL must be Zenable MCP endpoint: {ZENABLE_MCP_ENDPOINT}, got '{v}'"
            )
        return v

    @field_validator("disabled")
    def validate_disabled(cls, v):
        if v is not False:
            raise ValueError(f"Amazon Q MCP must have disabled=false, got {v}")
        return v

    @field_validator("headers")
    def validate_headers(cls, v):
        if not v:
            raise ValueError("Headers cannot be empty")
        if "API_KEY" not in v:
            raise ValueError("Headers must include API_KEY")
        if not v.get("API_KEY"):
            raise ValueError("API_KEY header cannot be empty")
        return v


class _MCPConfigFile(BaseModel):
    """Model for the complete MCP configuration file."""

    mcpServers: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="MCP server configurations"
    )

    model_config = ConfigDict(
        strict=False, extra="allow"
    )  # Allow additional top-level fields
