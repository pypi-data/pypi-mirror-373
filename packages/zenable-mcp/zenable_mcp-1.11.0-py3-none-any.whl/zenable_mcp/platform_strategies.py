import os
import platform
import shutil
from pathlib import Path
from typing import Optional, Protocol, runtime_checkable

from zenable_mcp.logging.logged_echo import echo
from zenable_mcp.logging.persona import Persona


@runtime_checkable
class PlatformStrategy(Protocol):
    """Protocol for platform-specific installation checks."""

    def check_application_installed(self, app_paths: list[str]) -> bool:
        """Check if an application is installed using platform-specific paths."""
        ...

    def get_user_config_base(self) -> Path:
        """Get the base directory for user configuration files."""
        ...

    def check_command_available(self, command: str) -> bool:
        """Check if a command is available in the system PATH."""
        ...

    def check_config_directory_exists(self, config_dir: Path) -> bool:
        """Check if a configuration directory exists."""
        ...

    def check_any_path_exists(self, paths: list[str]) -> bool:
        """Check if any of the given paths exist."""
        ...

    def resolve_path(self, path_spec: dict) -> Path:
        """Resolve a path specification to an absolute path.

        Args:
            path_spec: Path specification dictionary with platform-specific paths
                Expected format:
                {
                    'windows': {'base_path': '...', 'relative_path': '...'},
                    'linux': {'base_path': '...', 'relative_path': '...'},
                    'darwin': {'base_path': '...', 'relative_path': '...'}
                }
        """
        ...


class BasePlatformStrategy:
    """Base class with shared implementation for platform strategies."""

    def check_command_available(self, command: str) -> bool:
        """Check if a command is available in the system PATH."""
        return shutil.which(command) is not None

    def check_config_directory_exists(self, config_dir: Path) -> bool:
        """Check if a configuration directory exists."""
        return config_dir.exists()

    def check_any_path_exists(self, paths: list[str]) -> bool:
        """Check if any of the given paths exist."""
        return any(Path(path).exists() for path in paths)

    def resolve_path(self, path_spec: dict) -> Path:
        """Resolve a path specification to an absolute path - must be overridden."""
        raise NotImplementedError("Subclass must implement resolve_path")


class WindowsStrategy(BasePlatformStrategy):
    """Windows-specific platform strategy."""

    def check_application_installed(self, app_paths: list[str]) -> bool:
        """Check Windows-specific application paths."""
        # Check common Windows installation paths
        program_files = [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
            os.environ.get("LOCALAPPDATA", ""),
        ]

        for base_dir in program_files:
            if base_dir:
                if self.check_any_path_exists(
                    [str(Path(base_dir) / path) for path in app_paths]
                ):
                    return True

        # Also check if any provided absolute paths exist
        return self.check_any_path_exists(app_paths)

    def get_user_config_base(self) -> Path:
        """Get Windows user configuration base directory."""
        return Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))

    def resolve_path(self, path_spec: dict) -> Path:
        """Resolve a path specification to an absolute path on Windows."""
        windows_spec = path_spec.get("windows", {})

        # Determine the base path
        base_path_type = windows_spec.get("base_path", "appdata")

        if base_path_type == "appdata":
            appdata = os.environ.get("APPDATA")
            if not appdata:
                echo(
                    "APPDATA environment variable not set, using default",
                    persona=Persona.DEVELOPER,
                    err=True,
                )
                base = Path.home() / "AppData" / "Roaming"
            else:
                base = Path(appdata)
        elif base_path_type == "localappdata":
            localappdata = os.environ.get("LOCALAPPDATA")
            if not localappdata:
                echo(
                    "LOCALAPPDATA environment variable not set, using default",
                    persona=Persona.DEVELOPER,
                    err=True,
                )
                base = Path.home() / "AppData" / "Local"
            else:
                base = Path(localappdata)
        elif base_path_type == "home":
            base = Path.home()
        else:
            # If it's a custom path, use it directly
            base = Path(base_path_type).expanduser()

        # Combine with the relative path
        relative_path = windows_spec.get("relative_path", "")
        if relative_path:
            return base / relative_path
        return base


class LinuxStrategy(BasePlatformStrategy):
    """Linux-specific platform strategy."""

    def check_application_installed(self, app_paths: list[str]) -> bool:
        """Check Linux-specific application paths."""
        # Check common Linux installation paths
        linux_paths = [
            "/usr/local/bin",
            "/usr/bin",
            "/opt",
            str(Path.home() / ".local" / "bin"),
            str(Path.home() / ".local" / "share" / "applications"),
        ]

        for base_dir in linux_paths:
            if self.check_any_path_exists(
                [str(Path(base_dir) / path) for path in app_paths]
            ):
                return True

        # Check if desktop file exists
        desktop_files = [f"{path}.desktop" for path in app_paths]
        if self.check_any_path_exists(
            [
                str(Path.home() / ".local" / "share" / "applications" / df)
                for df in desktop_files
            ]
        ):
            return True

        # Also check if any provided absolute paths exist
        return self.check_any_path_exists(app_paths)

    def get_user_config_base(self) -> Path:
        """Get Linux user configuration base directory."""
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config)
        return Path.home() / ".config"

    def resolve_path(self, path_spec: dict) -> Path:
        """Resolve a path specification to an absolute path on Linux."""
        linux_spec = path_spec.get("linux", {})

        # Determine the base path
        base_path_type = linux_spec.get("base_path", "xdg_config")

        if base_path_type == "xdg_config":
            xdg_config = os.environ.get("XDG_CONFIG_HOME")
            if not xdg_config:
                echo(
                    "XDG_CONFIG_HOME environment variable not set, using default",
                    persona=Persona.DEVELOPER,
                    err=True,
                )
                base = Path.home() / ".config"
            else:
                base = Path(xdg_config)
        elif base_path_type == "xdg_data":
            xdg_data = os.environ.get("XDG_DATA_HOME")
            if not xdg_data:
                echo(
                    "XDG_DATA_HOME environment variable not set, using default",
                    persona=Persona.DEVELOPER,
                    err=True,
                )
                base = Path.home() / ".local" / "share"
            else:
                base = Path(xdg_data)
        elif base_path_type == "home":
            base = Path.home()
        else:
            # If it's a custom path, use it directly
            base = Path(base_path_type).expanduser()

        # Combine with the relative path
        relative_path = linux_spec.get("relative_path", "")
        if relative_path:
            return base / relative_path
        return base


class MacOSStrategy(BasePlatformStrategy):
    """macOS-specific platform strategy."""

    def check_application_installed(self, app_paths: list[str]) -> bool:
        """Check macOS-specific application paths."""
        # Check Applications folder
        app_names = [
            f"{path}.app" if not path.endswith(".app") else path for path in app_paths
        ]
        mac_paths = []
        for app in app_names:
            mac_paths.extend(
                [
                    f"/Applications/{app}",
                    str(Path.home() / "Applications" / app),
                    f"/System/Applications/{app}",
                ]
            )

        return self.check_any_path_exists(mac_paths)

    def get_user_config_base(self) -> Path:
        """Get macOS user configuration base directory."""
        return Path.home() / "Library" / "Application Support"

    def resolve_path(self, path_spec: dict) -> Path:
        """Resolve a path specification to an absolute path on macOS."""
        darwin_spec = path_spec.get("darwin", {})

        # Determine the base path
        base_path_type = darwin_spec.get("base_path", "application_support")

        if base_path_type == "application_support":
            base = Path.home() / "Library" / "Application Support"
        elif base_path_type == "preferences":
            base = Path.home() / "Library" / "Preferences"
        elif base_path_type == "home":
            base = Path.home()
        else:
            # If it's a custom path, use it directly
            base = Path(base_path_type).expanduser()

        # Combine with the relative path
        relative_path = darwin_spec.get("relative_path", "")
        if relative_path:
            return base / relative_path
        return base


def get_platform_strategy() -> PlatformStrategy:
    """Get the appropriate platform strategy for the current OS."""
    system = platform.system().lower()

    if system == "windows":
        return WindowsStrategy()
    elif system == "linux":
        return LinuxStrategy()
    elif system == "darwin":  # macOS
        return MacOSStrategy()
    else:
        # Default to Linux strategy for unknown platforms
        return LinuxStrategy()


def is_ide_installed(
    app_names: list[str],
    commands: list[str],
    config_dirs: list[str],
    strategy: Optional[PlatformStrategy] = None,
    ide_name: Optional[str] = None,
) -> bool:
    """
    Generic function to check if an IDE is installed.

    Args:
        app_names: List of application names to check (without .app extension on macOS)
        commands: List of command-line commands to check
        config_dirs: List of configuration directory names (relative to home)
        strategy: Optional platform strategy (defaults to current platform)
        ide_name: Optional IDE name for logging purposes

    Returns:
        True if the IDE is detected as installed, False otherwise
    """
    if strategy is None:
        strategy = get_platform_strategy()

    # For logging purposes
    ide_display = ide_name if ide_name else "IDE"
    checked_locations = []

    # Check if application is installed via platform-specific paths
    if app_names:
        checked_locations.append(f"application paths ({', '.join(app_names)})")
        if strategy.check_application_installed(app_names):
            echo(
                f"Detected {ide_display} is installed via application path",
                persona=Persona.POWER_USER,
                log=True,
            )
            return True

    # Check if any command is available
    for command in commands:
        checked_locations.append(f"command '{command}'")
        if strategy.check_command_available(command):
            echo(
                f"Detected {ide_display} is installed via command '{command}'",
                persona=Persona.POWER_USER,
                log=True,
            )
            return True

    # Check if any config directory exists
    for config_dir in config_dirs:
        config_path = Path.home() / config_dir
        checked_locations.append(f"config directory '{config_path}'")
        if strategy.check_config_directory_exists(config_path):
            echo(
                f"Detected {ide_display} is installed via config directory '{config_path}'",
                persona=Persona.POWER_USER,
                log=True,
            )
            return True

    # IDE not found - log what was checked
    if checked_locations:
        echo(
            f"{ide_display} does not seem to be installed after checking: {', '.join(checked_locations)}",
            persona=Persona.POWER_USER,
            log=True,
        )

    return False
