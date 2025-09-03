import json
import os
import platform
import re
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Protocol, runtime_checkable

# fcntl is only available on Unix-like systems
if sys.platform != "win32":
    import fcntl

    HAS_FCNTL = True
else:
    HAS_FCNTL = False


@runtime_checkable
class LoggingStrategy(Protocol):
    """Protocol for platform-specific logging strategies."""

    def get_log_directory(self) -> Path:
        """Get the platform-specific log directory."""
        ...

    def get_log_file_path(self) -> Path:
        """Get the full path to the log file."""
        ...

    def should_cleanup(self, log_file: Path, max_size_mb: float) -> bool:
        """Check if log cleanup is needed."""
        ...

    def cleanup_log(self, log_file: Path) -> None:
        """Perform log cleanup."""
        ...


class BaseLoggingStrategy(ABC):
    """Base class for platform-specific logging strategies."""

    def __init__(self, app_name: str = "zenable_mcp"):
        self.app_name = app_name
        self.max_size_mb = 5.0  # 5MB max total for all logs
        self.log_file_name = f"{app_name}.log"

    @abstractmethod
    def get_log_directory(self) -> Path:
        """Get the platform-specific log directory."""
        pass

    def get_log_file_path(self) -> Path:
        """Get the full path to the log file."""
        log_dir = self.get_log_directory()
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir / self.log_file_name

    def should_cleanup(self, log_file: Path, max_size_mb: float = None) -> bool:
        """Check if we need to manage log space (ring buffer approach)."""
        if max_size_mb is None:
            max_size_mb = self.max_size_mb

        if not log_file.exists():
            return False

        # Calculate total size of all log files
        total_size_mb = self._get_total_log_size(log_file) / (1024 * 1024)
        return total_size_mb >= max_size_mb

    def cleanup_log(self, log_file: Path) -> None:
        """Manage log space using ring buffer approach - remove oldest content.

        Uses file locking to prevent race conditions when multiple processes
        or threads access the log file simultaneously (on Unix-like systems).
        On Windows, file locking is skipped but the same logic is applied.
        """
        if not log_file.exists():
            return

        try:
            # Open file for reading and writing
            with open(log_file, "r+", encoding="utf-8") as f:
                # Acquire exclusive lock on Unix-like systems
                if HAS_FCNTL:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)

                try:
                    # Read all log lines
                    f.seek(0)
                    lines = f.readlines()

                    if not lines:
                        return

                    # Calculate how much to keep (75% to make room)
                    total_size = sum(len(line.encode("utf-8")) for line in lines)
                    target_size = int(
                        self.max_size_mb * 1024 * 1024 * 0.75
                    )  # Keep 75% to make room

                    # Remove oldest lines until we're under target size
                    current_size = total_size
                    lines_to_keep = lines.copy()

                    while current_size > target_size and len(lines_to_keep) > 1:
                        removed_line = lines_to_keep.pop(0)
                        current_size -= len(removed_line.encode("utf-8"))

                    # Write back the remaining lines
                    f.seek(0)
                    f.writelines(lines_to_keep)
                    f.truncate()  # Remove any remaining content after the new end

                finally:
                    # Release the lock on Unix-like systems
                    if HAS_FCNTL:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        except Exception:
            # Failed to manage log space
            print(f"CRITICAL Error: Unable to cleanup the log {log_file}")

    def _get_total_log_size(self, log_file: Path) -> int:
        """Get total size of the main log file in bytes."""
        if not log_file.exists():
            return 0
        return log_file.stat().st_size


class WindowsLoggingStrategy(BaseLoggingStrategy):
    """Windows-specific logging strategy."""

    def get_log_directory(self) -> Path:
        """Get Windows log directory in AppData/Local."""
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / self.app_name / "logs"
        return Path.home() / "AppData" / "Local" / self.app_name / "logs"


class MacOSLoggingStrategy(BaseLoggingStrategy):
    """macOS-specific logging strategy."""

    def get_log_directory(self) -> Path:
        """Get macOS log directory in ~/Library/Logs."""
        return Path.home() / "Library" / "Logs" / self.app_name


class LinuxLoggingStrategy(BaseLoggingStrategy):
    """Linux-specific logging strategy."""

    def get_log_directory(self) -> Path:
        """Get Linux log directory following XDG Base Directory specification."""
        xdg_cache = os.environ.get("XDG_CACHE_HOME")
        if xdg_cache:
            return Path(xdg_cache) / self.app_name / "logs"
        return Path.home() / ".cache" / self.app_name / "logs"


class LocalLogger:
    """Main logger class that uses strategy pattern for platform-specific logging."""

    def __init__(self, strategy: Optional[LoggingStrategy] = None):
        """Initialize the local logger with a platform-specific strategy."""
        if strategy is None:
            strategy = self._get_default_strategy()
        self.strategy = strategy
        self._ensure_log_file()

    def _get_default_strategy(self) -> LoggingStrategy:
        """Get the appropriate logging strategy for the current platform."""
        system = platform.system().lower()

        if system == "windows":
            return WindowsLoggingStrategy()
        elif system == "darwin":  # macOS
            return MacOSLoggingStrategy()
        elif system == "linux":
            return LinuxLoggingStrategy()
        else:
            # Default to Linux strategy for unknown platforms
            return LinuxLoggingStrategy()

    def _ensure_log_file(self) -> None:
        """Ensure the log file exists and manage space if needed."""
        log_file = self.strategy.get_log_file_path()

        # Create the file if it doesn't exist
        if not log_file.exists():
            log_file.parent.mkdir(parents=True, exist_ok=True)
            log_file.touch()
        # Check if we need to free up space
        elif self.strategy.should_cleanup(log_file, self.strategy.max_size_mb):
            self.strategy.cleanup_log(log_file)

    def _sanitize_data(self, data: Any) -> Any:
        """Recursively sanitize api_key from logs."""
        if isinstance(data, dict):
            sanitized = {}
            for k, v in data.items():
                # Check if this key is api_key and redact its value
                if k == "api_key":
                    sanitized[k] = "***REDACTED***"
                else:
                    sanitized[k] = self._sanitize_data(v)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        elif isinstance(data, str):
            # Also check for api_key in string values (e.g., in JSON strings)
            return re.sub(r'("api_key"\s*:\s*")[^"]*(")', r"\1***REDACTED***\2", data)
        else:
            return data

    def log_command(
        self,
        command: str,
        args: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ) -> None:
        """Log a command execution with its arguments and result."""
        # Sanitize the args to remove api_key
        sanitized_args = self._sanitize_data(args)
        sanitized_result = self._sanitize_data(result) if result is not None else None
        sanitized_error = self._sanitize_data(error) if error is not None else None

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "args": sanitized_args,
            "platform": platform.system(),
            "python_version": platform.python_version(),
        }

        if sanitized_result is not None:
            log_entry["result"] = sanitized_result

        if sanitized_error is not None:
            log_entry["error"] = sanitized_error

        if duration_ms is not None:
            log_entry["duration_ms"] = duration_ms

        log_file = None
        try:
            log_file = self.strategy.get_log_file_path()

            # Ensure file exists
            if not log_file.exists():
                log_file.parent.mkdir(parents=True, exist_ok=True)
                log_file.touch()

            # Write the new entry with file locking
            new_entry = json.dumps(log_entry) + "\n"
            new_entry_size = len(new_entry.encode("utf-8"))

            # Check if adding this entry would exceed limit
            current_size = self.strategy._get_total_log_size(log_file)
            max_size_bytes = self.strategy.max_size_mb * 1024 * 1024

            if current_size + new_entry_size > max_size_bytes:
                # Need to make room
                self.strategy.cleanup_log(log_file)

            # Append the log entry with exclusive lock on Unix-like systems
            with open(log_file, "a", encoding="utf-8") as f:
                # Acquire exclusive lock for appending on Unix-like systems
                if HAS_FCNTL:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.write(new_entry)
                finally:
                    # Release the lock on Unix-like systems
                    if HAS_FCNTL:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        except Exception:
            # Failed to manage log space
            if log_file:
                print(f"CRITICAL Error: Unable to cleanup the log {log_file}")
            else:
                print("CRITICAL Error: Unable to get log file path")

    def log_raw(self, message: str) -> None:
        """Log a raw message (for backwards compatibility)."""
        self.log_command(command="raw_log", args={"message": message}, result=None)


# Global logger instance
_local_logger: Optional[LocalLogger] = None


def get_local_logger() -> LocalLogger:
    """Get or create the global local logger instance."""
    global _local_logger
    if _local_logger is None:
        _local_logger = LocalLogger()
    return _local_logger


def log_command_execution(
    command: str,
    args: Dict[str, Any],
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    duration_ms: Optional[float] = None,
) -> None:
    """Convenience function to log command execution."""
    logger = get_local_logger()
    logger.log_command(command, args, result, error, duration_ms)
