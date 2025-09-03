"""
CodeMie SDK for Python
~~~~~~~~~~~~~~~~~~~~~

A Python SDK for interacting with CodeMie API.

Basic usage:

    >>> from codemie_sdk import CodeMieClient
    >>> client = CodeMieClient(
    ...     auth_server_url="https://auth.example.com",
    ...     auth_client_id="client_id",
    ...     auth_client_secret="secret",
    ...     auth_realm_name="realm",
    ...     codemie_api_domain="api.codemie.com"
    ... )
    >>> assistants = client.assistants.list()
"""

from .client.client import CodeMieClient

__version__ = "0.1.25"
__all__ = ["CodeMieClient"]
