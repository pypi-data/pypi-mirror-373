"""
API module for result parser agent.

Provides the registry client for interacting with the parser registry API.
"""

from .registry_client import RegistryClient, create_registry_client

__all__ = ["RegistryClient", "create_registry_client"]
