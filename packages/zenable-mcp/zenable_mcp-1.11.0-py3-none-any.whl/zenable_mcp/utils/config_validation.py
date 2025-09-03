"""Configuration validation utilities."""

from typing import Optional

from pydantic import ValidationError

from zenable_mcp.ide_config import create_ide_config
from zenable_mcp.models.mcp_config import _ZenableMCPConfig
from zenable_mcp.utils.install_status import ConfigStatus
from zenable_mcp.utils.validation_errors import format_validation_error


def _create_config_status(
    is_configured: bool, is_compatible: bool, details: Optional[str] = None
) -> ConfigStatus:
    """Helper to safely create ConfigStatus with error handling."""
    try:
        return ConfigStatus(
            is_configured=is_configured, is_compatible=is_compatible, details=details
        )
    except ValidationError as e:
        raise ValueError("Failed to create ConfigStatus") from e


def check_zenable_config_status(
    existing_config: dict,
    ide_name: Optional[str] = None,
    api_key: Optional[str] = None,
) -> ConfigStatus:
    """Check if Zenable configuration exists and is properly configured.

    Args:
        existing_config: The existing configuration dictionary
        ide_name: Optional IDE name for specific validation
        api_key: Optional API key for creating IDE config

    Returns:
        ConfigStatus object with:
        - is_configured: True if Zenable is configured
        - is_compatible: True if the configuration matches expectations
        - details: Optional details about incompatible configuration
    """
    # Check if Zenable server exists
    if "mcpServers" not in existing_config:
        return _create_config_status(is_configured=False, is_compatible=False)

    if "zenable" not in existing_config.get("mcpServers", {}):
        return _create_config_status(is_configured=False, is_compatible=False)

    # Configuration exists, now check if it's compatible
    if ide_name and api_key:
        try:
            # Create IDE config and use its validation method
            ide_config = create_ide_config(ide_name, api_key, is_global=False)
            config_status = ide_config.check_config_status(existing_config)

            # Legacy configs are considered compatible (they can be upgraded)
            if config_status in ["compatible", "legacy"]:
                return _create_config_status(is_configured=True, is_compatible=True)

            # For incompatible configs, try to get more specific error
            # First try current model, then fall back to legacy models
            zenable_config = existing_config["mcpServers"]["zenable"]
            validation_errors = []

            try:
                model_class = ide_config.get_validation_model()
                model_class.model_validate(zenable_config)
            except (ValidationError, ValueError, TypeError, AttributeError) as e:
                validation_errors.append(format_validation_error(e))

            # If current model failed, try legacy models
            if hasattr(ide_config, "_legacy_models"):
                for legacy_model in ide_config._legacy_models:
                    try:
                        legacy_model.model_validate(zenable_config)
                        # Legacy model validates - it's actually a legacy config
                        return _create_config_status(
                            is_configured=True, is_compatible=True
                        )
                    except (ValidationError, ValueError, TypeError, AttributeError):
                        # Continue to next legacy model
                        continue

            # No models validated successfully
            return _create_config_status(
                is_configured=True,
                is_compatible=False,
                details=validation_errors[0]
                if validation_errors
                else "Invalid configuration",
            )

        except ValueError:
            # Unknown IDE, fall back to basic check
            pass

    # Fallback: Use basic Zenable MCP validation model
    zenable_config = existing_config["mcpServers"]["zenable"]

    try:
        # Validate using the base Zenable model
        _ZenableMCPConfig.model_validate(zenable_config)
        return _create_config_status(is_configured=True, is_compatible=True)
    except (ValidationError, ValueError, TypeError, AttributeError) as e:
        return _create_config_status(
            is_configured=True,
            is_compatible=False,
            details=format_validation_error(e),
        )
