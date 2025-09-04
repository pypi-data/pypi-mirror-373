"""A client library for accessing OWASP Dependency-Track"""

from .client import AuthenticatedClient, Client

__all__ = (
    "AuthenticatedClient",
    "Client",
)
