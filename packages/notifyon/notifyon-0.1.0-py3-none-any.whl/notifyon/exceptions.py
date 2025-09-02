"""
Exception classes for NotifyOn SDK
"""


class NotifyOnError(Exception):
    """Base exception for NotifyOn SDK errors"""
    pass


class ConfigurationError(NotifyOnError):
    """Raised when there's a configuration issue"""
    pass


class APIError(NotifyOnError):
    """Raised when the API returns an error"""
    pass