"""Authentication credentials module for CodeMie SDK."""

import os

import requests
from typing import Optional


class KeycloakCredentials:
    """Keycloak authentication credentials handler."""

    def __init__(
        self,
        server_url: str,
        realm_name: str,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify_ssl: bool = True,
    ):
        """Initialize Keycloak credentials.

        Args:
            server_url: Keycloak server URL
            realm_name: Realm name
            client_id: Client ID (optional if using username/password)
            client_secret: Client secret (optional if using username/password)
            username: Username/email for password grant (optional)
            password: Password for password grant (optional)
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        self.server_url = server_url.rstrip("/")
        self.realm_name = realm_name
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl

        if os.getenv("ENV", "").lower() != "local" and not (
            (client_id and client_secret) or (username and password)
        ):
            raise ValueError(
                "Either client credentials (client_id, client_secret) or "
                "user credentials (username, password) must be provided"
            )

    def get_token(self) -> str:
        if os.getenv("ENV", "").lower() == "local":
            return ""
        """Get access token using either client credentials or password grant."""
        url = (
            f"{self.server_url}/realms/{self.realm_name}/protocol/openid-connect/token"
        )

        if self.username and self.password:
            # Use Resource Owner Password Credentials flow
            payload = {
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
                "client_id": self.client_id
                or "codemie-sdk",  # Use default client if not specified
            }
            if self.client_secret:
                payload["client_secret"] = self.client_secret
        else:
            # Use Client Credentials flow
            payload = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }

        response = requests.post(url, data=payload, verify=self.verify_ssl)
        response.raise_for_status()
        return response.json()["access_token"]

    def exchange_token_for_user(self, email: str, access_token: str) -> str:
        """Exchange service account token for user token."""
        user_id = self.find_user_by_email(email, access_token)
        return self._exchange_token_for_user(user_id, access_token)

    def find_user_by_email(self, email: str, access_token: str) -> str:
        """Find user ID by email."""
        url = f"{self.server_url}/admin/realms/{self.realm_name}/users?email={email}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers, verify=self.verify_ssl)
        response.raise_for_status()

        users = response.json()
        if not users:
            raise ValueError(f"User with email {email} not found")
        return users[0]["id"]

    def _exchange_token_for_user(self, user_id: str, service_account_token: str) -> str:
        """Exchange token for specific user."""
        url = (
            f"{self.server_url}/realms/{self.realm_name}/protocol/openid-connect/token"
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "urn:ietf:params:oauth:grant-datasource_type:token-exchange",
            "subject_token": service_account_token,
            "requested_subject": user_id,
        }

        response = requests.post(
            url, headers=headers, data=payload, verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()["access_token"]
