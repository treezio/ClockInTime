"""
ClockInTime - Automatic Factorial clock in/out for macOS.

A lightweight menu bar application that automatically clocks in when you
log into your Mac and clocks out when you log out or put it to sleep.
"""

from .constants import APP_NAME, APP_VERSION
from .exceptions import APIError, AuthenticationError, ClockInTimeError, ConfigurationError, SystemEventError

__version__ = APP_VERSION
__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "APIError",
    "AuthenticationError",
    "ClockInTimeError",
    "ConfigurationError",
    "SystemEventError",
]
