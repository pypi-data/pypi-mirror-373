"""exceptions.py.

This module defines custom exceptions for the TopQADClient SDK.
"""


class TopQADError(Exception):
    """Base exception for all TopQADClient errors."""

    pass


class TopQADHTTPError(TopQADError):
    """Raised for HTTP-related errors."""

    pass


class TopQADRuntimeError(TopQADError):
    """Raised for runtime errors."""

    pass


class TopQADTimeoutError(TopQADError):
    """
    Raised when a job takes longer to return a result than the configured polling
    interval and max attempts.
    """

    pass


class TopQADValueError(TopQADError):
    """Raised for validation/type errors."""

    pass


class TopQADSchemaError(TopQADError):
    """Raised for schema validation errors."""

    pass


class TopQADBetaVersionError(TopQADError):
    """Raised for errors relating to features that are not available for Beta users."""

    pass


class MissingRefreshToken(TopQADError):
    """Exception raised when the TOPQAD_REFRESH_TOKEN environment variable is missing."""

    pass
