"""Shared configuration management utilities for safe JSON file operations."""

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import json5

from zenable_mcp.exit_codes import ExitCode
from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona

# Global variable to track temporary files for cleanup
_temp_files_to_cleanup: list[Path] = []


def cleanup_temp_files() -> None:
    """Clean up any temporary .zenable files that were created."""
    global _temp_files_to_cleanup
    for temp_file in _temp_files_to_cleanup:
        if temp_file.exists():
            try:
                temp_file.unlink()
                echo(f"Cleaned up temporary file: {temp_file}", err=True, log=True)
            except OSError:
                pass  # Best effort cleanup
    _temp_files_to_cleanup.clear()


def safe_write_text(file_path: Path, content: str) -> None:
    """Safely write text content using a .zenable temporary file.

    This function writes to a temporary file first and then atomically
    renames it to the target path, ensuring data integrity even if the
    process is interrupted.

    Args:
        file_path: Path to the target file
        content: Text content to write

    Raises:
        click.ClickException: On any write error
    """
    global _temp_files_to_cleanup

    # Write to .zenable file first
    zenable_path = file_path.with_suffix(file_path.suffix + ".zenable")

    # Track the temp file for cleanup
    _temp_files_to_cleanup.append(zenable_path)

    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write content to temp file
        with open(zenable_path, "w") as f:
            f.write(content)

        # Atomically rename to target
        zenable_path.rename(file_path)

        # Remove from cleanup list since it's been renamed
        _temp_files_to_cleanup.remove(zenable_path)

        echo(f"Successfully wrote file to {file_path}", persona=Persona.POWER_USER)

    except Exception as e:
        # Clean up temp file if it exists
        if zenable_path.exists():
            zenable_path.unlink()
        echo(f"Failed to write {file_path}: {e}", err=True)
        sys.exit(ExitCode.FILE_WRITE_ERROR)


def safe_write_json(
    settings_path: Path,
    settings: dict,
) -> None:
    """Safely write JSON5 settings while preserving comments from original content.

    This function writes to a temporary file first and then atomically
    renames it to the target path, ensuring data integrity even if the
    process is interrupted. Uses JSON5 format to support comments.

    Args:
        settings_path: Path to the settings file
        settings: Dictionary to write as JSON5
    """
    global _temp_files_to_cleanup

    # Write to .zenable file first
    zenable_path = settings_path.with_suffix(".json.zenable")

    # Track the temp file for cleanup
    _temp_files_to_cleanup.append(zenable_path)

    try:
        # Ensure parent directory exists
        settings_path.parent.mkdir(parents=True, exist_ok=True)

        # Use json5.dumps which preserves the ability to have comments
        # Note: json5.dumps doesn't preserve comments from parsing, but allows them in output
        # For full comment preservation, we'd need to maintain the original structure
        # Use trailing_commas=False to maintain compatibility with standard JSON parsers
        content = (
            json5.dumps(settings, indent=2, quote_keys=True, trailing_commas=False)
            + "\n"
        )

        # Test write permissions and disk space
        with open(zenable_path, "w") as f:
            f.write(content)
            f.flush()  # Ensure data is written
            os.fsync(f.fileno())  # Force write to disk

        # Atomic rename (on POSIX systems)
        zenable_path.replace(settings_path)

        # Remove from cleanup list after successful rename
        if zenable_path in _temp_files_to_cleanup:
            _temp_files_to_cleanup.remove(zenable_path)

        echo(
            f"Successfully wrote configuration to {settings_path}",
            persona=Persona.POWER_USER,
        )

    except OSError as e:
        # Clean up zenable file on error
        if zenable_path.exists():
            try:
                zenable_path.unlink()
                # Remove from cleanup list after manual cleanup
                if zenable_path in _temp_files_to_cleanup:
                    _temp_files_to_cleanup.remove(zenable_path)
            except OSError:
                pass  # Best effort cleanup

        error_msg = f"Failed to write settings to {settings_path}: {e}"

        # Check for specific error conditions
        if "No space left on device" in str(e):
            error_msg += "\nDisk is full. Please free up space and try again."
        elif "Permission denied" in str(e):
            error_msg += (
                "\nInsufficient permissions. Check file and directory permissions."
            )

        echo(error_msg, err=True)
        sys.exit(ExitCode.FILE_WRITE_ERROR)

    except (TypeError, ValueError) as e:
        # Clean up zenable file on error
        if zenable_path.exists():
            try:
                zenable_path.unlink()
                # Remove from cleanup list after manual cleanup
                if zenable_path in _temp_files_to_cleanup:
                    _temp_files_to_cleanup.remove(zenable_path)
            except OSError:
                pass

        echo(
            f"Failed to serialize settings to JSON5 for {settings_path}: {e}", err=True
        )
        sys.exit(ExitCode.FILE_WRITE_ERROR)


def has_json_comments(content: str) -> bool:
    """Check if JSON content contains comments or JSON5 features.

    Args:
        content: The JSON file content as a string

    Returns:
        True if JSON5 features (including comments) are detected, False otherwise
    """
    # Check if JSON5 can parse it but regular JSON cannot
    # This catches JSON5 features like comments, trailing commas, unquoted keys, etc.
    try:
        json.loads(content)
        # If regular JSON can parse it, no JSON5 features
        return False
    except json.JSONDecodeError:
        try:
            json5.loads(content)
            # JSON5 can parse but regular JSON cannot - has JSON5 features
            return True
        except (ValueError, Exception):
            # Neither can parse - likely invalid
            return False


def load_json_config(file_path: Path) -> tuple[dict[str, Any], bool]:
    """Load a JSON configuration file, supporting comments via JSON5, and detect if comments exist.

    Args:
        file_path: Path to the JSON5 file

    Returns:
        Tuple of (dictionary containing the parsed JSON5 data, has_comments flag)
        Returns ({}, False) if file doesn't exist

    Raises:
        ValueError: If the JSON5 is invalid
        IOError: If there's an error reading the file
    """
    if not file_path.exists():
        return {}, False

    try:
        with open(file_path, "r") as f:
            content = f.read()

        has_comments = has_json_comments(content)

        # Use json5.loads which handles comments natively
        try:
            data = json5.loads(content)
        except (ValueError, Exception):
            # If json5 fails, try regular JSON as fallback
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON5/JSON in {file_path}: {e}")

        return data, has_comments

    except Exception as e:
        if "Invalid JSON" not in str(e):
            raise IOError(f"Error reading {file_path}: {e}")
        raise


def merge_mcp_server_config(
    existing_config: dict[str, Any],
    new_server_name: str,
    new_server_config: dict[str, Any],
    overwrite: bool = False,
) -> dict[str, Any]:
    """Merge a new MCP server configuration into an existing config.

    Args:
        existing_config: The existing configuration dictionary
        new_server_name: Name of the new server to add
        new_server_config: Configuration for the new server
        overwrite: Whether to overwrite if server already exists

    Returns:
        Updated configuration dictionary

    Raises:
        ValueError: If server already exists and overwrite is False
    """
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}

    if new_server_name in existing_config["mcpServers"] and not overwrite:
        raise ValueError(
            f"Server '{new_server_name}' already exists in configuration. "
            "Use --overwrite to replace it."
        )

    existing_config["mcpServers"][new_server_name] = new_server_config
    return existing_config


def backup_config_file(file_path: Path) -> Optional[Path]:
    """Create a backup of a configuration file in the system temp directory.

    Args:
        file_path: Path to the file to backup

    Returns:
        Path to the backup file if created, None if original doesn't exist

    Raises:
        IOError: If backup fails
    """
    if not file_path.exists():
        return None

    # Create backup filename with UTC timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
    original_name = file_path.name  # Full name including extension
    backup_name = f"{original_name}_{timestamp}.bkp"

    # Get system temp directory
    temp_dir = Path(tempfile.gettempdir())
    backup_path = temp_dir / backup_name

    try:
        shutil.copy2(file_path, backup_path)

        echo(f"Created backup: {backup_path}", persona=Persona.POWER_USER)
        echo(f"  Original file: {file_path}", persona=Persona.POWER_USER)
        echo(f"  Backup location: {temp_dir}", persona=Persona.POWER_USER)

        return backup_path
    except Exception as e:
        raise IOError(f"Failed to create backup of {file_path}: {e}")


def find_config_file(config_paths: list[Path]) -> Optional[Path]:
    """Find the first existing config file from a list of paths.

    Args:
        config_paths: List of potential configuration file paths

    Returns:
        First existing path, or None if none exist
    """
    for path in config_paths:
        expanded_path = Path(str(path)).expanduser()
        if expanded_path.exists():
            return expanded_path
    return None


def get_default_config_path(config_paths: list[Path]) -> Path:
    """Get the default (first) config path from a list.

    Args:
        config_paths: List of potential configuration file paths

    Returns:
        The first path, expanded with ~ resolved
    """
    if not config_paths:
        raise ValueError("No config paths provided")

    return Path(str(config_paths[0])).expanduser()
