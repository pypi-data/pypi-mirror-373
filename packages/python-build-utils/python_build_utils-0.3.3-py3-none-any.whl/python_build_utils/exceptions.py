"""Custom exceptions for the python_build_utils package."""

from .constants import PYD_FILE_FORMATS


class PydFileSuffixError(Exception):
    """Raised when a file does not have a .pyd suffix."""

    def __init__(self, filename: str) -> None:
        """Initialize the error with the filename that lacks a .pyd suffix."""
        message = f"The file '{filename}' is not of type '.pyd'. Quitting."
        super().__init__(message)


class PydFileFormatError(Exception):
    """Raised when a .pyd file does not match the expected naming format."""

    def __init__(self, filename: str) -> None:
        """Initialize the error with the filename that has an invalid format."""
        message = (
            f"File information could not be extracted from '{filename}'.\n"
            "Supported formats:\n"
            f"  • {PYD_FILE_FORMATS['long']}\n"
            f"  • {PYD_FILE_FORMATS['short']}"
        )
        super().__init__(message)


class VersionNotFoundError(Exception):
    """Raised when no version is provided or extractable from the .pyd file."""

    def __init__(self) -> None:
        """Initialize the error when the version is not available."""
        message = (
            "No version could be extracted from the .pyd file.\n"
            "Please provide the version explicitly using '--package_version <version>'."
        )
        super().__init__(message)
