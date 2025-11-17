"""
Custom exceptions for ClockInTime application.
"""


class ClockInTimeError(Exception):
    """Base exception for all ClockInTime errors."""
    pass


class APIError(ClockInTimeError):
    """Raised when API operations fail."""
    pass


class AuthenticationError(APIError):
    """Raised when authentication fails."""
    pass


class ConfigurationError(ClockInTimeError):
    """Raised when configuration is invalid or missing."""
    pass


class SystemEventError(ClockInTimeError):
    """Raised when system event monitoring fails."""
    pass
