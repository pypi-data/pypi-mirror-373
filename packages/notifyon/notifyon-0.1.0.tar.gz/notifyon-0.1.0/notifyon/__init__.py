"""
NotifyOn Python SDK

A simple SDK for sending notifications when long-running agent tasks complete.
"""

from .client import NotifyOn
from .exceptions import NotifyOnError

__version__ = "0.1.0"
__all__ = ["NotifyOn", "NotifyOnError"]