"""Operation status codes for internal function returns."""

from enum import IntEnum


class OperationStatus(IntEnum):
    """Status codes for operation results that are not exit codes."""

    SUCCESS = 0
    FAILURE = 1
    NO_FILES_FOUND = 2
    ALREADY_EXISTS = 3
    PERMISSION_DENIED = 4
    INVALID_INPUT = 5
