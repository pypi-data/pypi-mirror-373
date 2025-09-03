"""Version checking utilities for zenable-mcp."""

import atexit
import json
import sys
import threading
from typing import Optional

import click
import requests

from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.utils.retries import retry_on_error


@retry_on_error(
    max_retries=2,  # Reduced retries for faster failure
    initial_delay=0.5,
    max_delay=2.0,  # Reduced max delay
    backoff_factor=2.0,
    exceptions=(requests.RequestException, TimeoutError, OSError),
)
def get_pypi_version(package_name: str = "zenable-mcp") -> Optional[str]:
    """
    Fetch the latest version of a package from PyPI.

    Args:
        package_name: The name of the package on PyPI

    Returns:
        The latest version string or None if unable to fetch
    """
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=2)
        response.raise_for_status()
        data = response.json()
        return data.get("info", {}).get("version")
    except (requests.RequestException, json.JSONDecodeError, KeyError, TimeoutError):
        return None


def parse_semver(version_str: str) -> Optional[tuple[int, ...]]:
    """
    Parse a semantic version string into a tuple of integers for comparison.

    Args:
        version_str: Version string like "1.2.0"

    Returns:
        Tuple of integers like (1, 2, 0), or None if parsing fails
    """
    try:
        if not version_str or not isinstance(version_str, str):
            return None
        parts = version_str.split(".")
        if not parts or not all(part.isdigit() for part in parts):
            return None
        return tuple(int(part) for part in parts)
    except (ValueError, AttributeError):
        return None


def check_for_updates_sync(current_version: str) -> Optional[str]:
    """
    Check if there's a newer version available on PyPI (synchronous version).

    Args:
        current_version: The current version of the package

    Returns:
        A formatted update message if an update is available, None otherwise
    """
    if not sys.stdout.isatty():
        # Don't show update notifications in non-interactive environments
        return None

    try:
        latest_version = get_pypi_version()
        if not latest_version:
            return None

        current_tuple = parse_semver(current_version)
        latest_tuple = parse_semver(latest_version)

        # Skip comparison if either version couldn't be parsed
        if current_tuple is None or latest_tuple is None:
            return None

        if latest_tuple > current_tuple:
            return (
                f"\nA new version is available: {current_version} -> {latest_version}\n"
                f"Run 'uvx --upgrade zenable-mcp' to update.\n"
            )
    except Exception:
        # Silently ignore any errors during version check
        pass

    return None


class VersionChecker:
    """Manages background version checking and notification.

    Why we use threading instead of asyncio:
    - Network I/O releases the GIL, so the check doesn't block CPU work on the main thread
    - No event loop to manage - much simpler for this straightforward use case
    - Works seamlessly with the requests library
    - Exceptions in threads are silently swallowed (which is actually preferred here -
      worst case is the user doesn't see an update notification)
    - If we need more complex async behavior in the future, we can switch to asyncio
    """

    def __init__(self):
        self.update_message: Optional[str] = None
        self._thread: Optional[threading.Thread] = None
        self._registered_atexit = False

    def _check_in_background(self, current_version: str) -> None:
        """Check for updates in the background thread.

        Any exceptions are silently ignored - it's better to not show an update
        notification than to disrupt the user's workflow with errors.
        """
        try:
            self.update_message = check_for_updates_sync(current_version)
        except Exception:
            # Silently ignore any errors - update notification is non-critical
            pass

    def start_check(self, current_version: str) -> None:
        """Start the version check in a background thread.

        Uses a daemon thread to ensure the check doesn't prevent program exit.
        The thread performs network I/O which releases the GIL, allowing the main
        thread to continue unimpeded.
        """
        # Run the check in a daemon thread
        self._thread = threading.Thread(
            target=self._check_in_background, args=(current_version,), daemon=True
        )
        self._thread.start()

        # Register the exit handler if not already done
        if not self._registered_atexit:
            atexit.register(self.display_update_notification)
            self._registered_atexit = True

    def display_update_notification(self) -> None:
        """Display the update notification if available."""
        # Wait for the thread to complete (with a short timeout)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)

        # Display the message if we have one
        if self.update_message:
            echo(
                click.style(self.update_message, fg="yellow"),
                err=True,
            )


# Global instance
_version_checker = VersionChecker()


def check_for_updates(current_version: str) -> None:
    """
    Start checking for updates in the background.
    The result will be displayed when the program exits.

    Args:
        current_version: The current version of the package
    """
    _version_checker.start_check(current_version)
