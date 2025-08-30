"""
ClickUp API client module.

This module provides the HTTP client abstraction for interacting with the ClickUp API.
It encapsulates all HTTP operations and error handling, providing a clean interface
for tools to consume.
"""

from .api_client import ClickupApiClient

__all__ = ["ClickupApiClient"]
