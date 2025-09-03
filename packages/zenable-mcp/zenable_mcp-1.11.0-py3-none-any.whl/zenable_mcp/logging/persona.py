"""Persona enum for different user types and their logging levels."""

from enum import Enum


class Persona(Enum):
    """Defines different user personas for logging purposes."""

    USER = "user"  # Regular users - outputs via logged_echo
    POWER_USER = "power_user"  # Power users - outputs via logging.info
    DEVELOPER = "developer"  # Developers - outputs via logging.debug
