"""Utilities for handling and formatting validation errors."""

import re
from typing import Optional

from pydantic import ValidationError


def format_validation_error(error: Exception) -> str:
    """Format a validation error into a user-friendly message.

    Args:
        error: The exception from Pydantic validation

    Returns:
        A user-friendly error message
    """
    if isinstance(error, ValidationError):
        # Parse Pydantic validation errors
        error_details = []
        for err in error.errors():
            field = err.get("loc", ())
            msg = err.get("msg", "")

            # Extract meaningful messages based on common patterns
            if "npx" in msg.lower():
                return "Not using npx command"
            elif "mcp-remote" in msg.lower():
                if "@latest" in msg:
                    return "Using pinned mcp-remote version (must use @latest)"
                return "Not using mcp-remote"
            elif "endpoint" in msg.lower() or "zenable.app" in msg.lower():
                return "Using different endpoint"
            elif "api_key" in msg.lower() or "api key" in msg.lower():
                return "Missing or incorrectly formatted API key"
            elif "conformance_check" in msg.lower():
                if "alwaysAllow" in str(field):
                    return "Missing 'conformance_check' in alwaysAllow"
                elif "autoApprove" in str(field):
                    return "Missing 'conformance_check' in autoApprove"
                return "Missing conformance_check configuration"
            elif "trust" in msg.lower():
                return "Missing or incorrect 'trust' setting"
            elif "disabled" in msg.lower():
                return "Server is disabled"

            # Add to details if no specific pattern matched
            if field:
                field_name = ".".join(str(f) for f in field)
                error_details.append(f"{field_name}: {msg}")
            else:
                error_details.append(msg)

        # If we collected details, return them
        if error_details:
            if len(error_details) == 1:
                return error_details[0]
            return "Multiple validation errors: " + "; ".join(error_details)

    # For non-ValidationError exceptions, extract meaningful patterns
    error_str = str(error)

    # Check for common patterns in error messages
    if "zenable mcp must use 'npx' command" in error_str.lower():
        return "Not using npx"
    elif "args must include 'mcp-remote'" in error_str.lower():
        return "Not using mcp-remote"
    elif "args must include zenable mcp endpoint" in error_str.lower():
        return "Using different endpoint"
    elif "args must include api_key header" in error_str.lower():
        return "Missing or incorrectly formatted API key"
    elif "mcp-remote must use @latest version" in error_str.lower():
        # Try to extract version if present
        version_match = re.search(r"got: mcp-remote@([^\s]+)", error_str)
        if version_match:
            return f"Using pinned mcp-remote version: {version_match.group(1)}"
        return "Using pinned mcp-remote version"
    elif "hook script must include 'zenable conformance_check'" in error_str.lower():
        return "Hook script missing 'zenable conformance_check'"
    elif "must have disabled=false" in error_str.lower():
        return "Server must not be disabled"
    elif "must have trust=true" in error_str.lower():
        return "Server must be trusted"
    elif "'conformance_check' in alwaysallow" in error_str.lower():
        return "Missing 'conformance_check' in alwaysAllow"
    elif "'conformance_check' in autoapprove" in error_str.lower():
        return "Missing 'conformance_check' in autoApprove"

    # Fallback to generic message
    return "Configuration validation failed"


def get_config_status_message(
    is_configured: bool, is_compatible: bool, error: Optional[Exception] = None
) -> Optional[str]:
    """Get a status message based on configuration state.

    Args:
        is_configured: Whether Zenable is configured at all
        is_compatible: Whether the configuration is compatible
        error: Optional exception from validation

    Returns:
        Status message or None if everything is OK
    """
    if not is_configured:
        return None  # Not configured

    if is_compatible:
        return None  # Configured and compatible

    # Configured but not compatible
    if error:
        return format_validation_error(error)

    return "Configuration exists but is not compatible"
