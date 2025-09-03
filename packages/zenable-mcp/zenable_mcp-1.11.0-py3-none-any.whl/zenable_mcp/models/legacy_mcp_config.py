"""Legacy Pydantic models for MCP configuration validation."""

import os
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Constants
ZENABLE_MCP_ENDPOINT = os.environ.get(
    "ZENABLE_API_ENDPOINT", "https://mcp.www.zenable.app/"
)


class _LegacyClaudeCodeMCPServerConfig(BaseModel):
    """Legacy Claude Code MCP server configuration (command-based format with mcp-remote).

    This was the original format used before SSE support was added.
    Example:
    {
        "command": "npx",
        "args": ["-y", "--", "mcp-remote@latest", "https://...", "--header", "API_KEY:..."]
    }
    """

    command: str = Field(..., description="The command to execute")
    args: list[str] = Field(..., description="Arguments for the command")

    model_config = ConfigDict(
        strict=False, extra="allow"
    )  # Allow additional fields for flexibility

    @field_validator("command")
    def validate_command(cls, v):
        if v != "npx":
            raise ValueError(
                f"Legacy Claude Code MCP must use 'npx' command, got '{v}'"
            )
        return v

    @field_validator("args")
    def validate_args(cls, v):
        if not v:
            raise ValueError("Args cannot be empty")

        # Check for required components
        args_str = " ".join(v)

        if "mcp-remote" not in args_str:
            raise ValueError("Args must include 'mcp-remote'")

        # Check for endpoint with or without trailing slash
        endpoint_base = ZENABLE_MCP_ENDPOINT.rstrip("/")
        if endpoint_base not in args_str:
            raise ValueError(
                f"Args must include Zenable MCP endpoint: {ZENABLE_MCP_ENDPOINT}"
            )

        # Check for API key
        has_api_key = any("API_KEY:" in arg for arg in v)
        if not has_api_key:
            raise ValueError("Args must include API_KEY header")

        return v


class _LegacyGenericMCPServerConfig(BaseModel):
    """Generic legacy MCP server configuration for all IDEs.

    This format was commonly used across different IDEs.
    Example:
    {
        "command": "npx",
        "args": ["-y", "zenable-mcp"],
        "env": {"ZENABLE_API_KEY": "..."}
    }
    """

    command: str = Field(..., description="The command to execute")
    args: list[str] = Field(..., description="Arguments for the command")
    env: Optional[dict[str, str]] = Field(
        default=None, description="Environment variables"
    )

    model_config = ConfigDict(
        strict=False, extra="allow"
    )  # Allow additional fields for flexibility

    @field_validator("command")
    def validate_command(cls, v):
        if v != "npx":
            raise ValueError(f"Legacy MCP must use 'npx' command, got '{v}'")
        return v

    @field_validator("args")
    def validate_args(cls, v):
        if not v:
            raise ValueError("Args cannot be empty")

        # Check for zenable-mcp in args
        args_str = " ".join(v)
        if "zenable-mcp" not in args_str:
            raise ValueError("Args must include 'zenable-mcp'")

        return v
