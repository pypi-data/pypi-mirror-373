"""Base client implementation for CodeMie SDK."""

from typing import Optional

from ..auth.credentials import KeycloakCredentials
from ..services.assistant import AssistantService
from ..services.datasource import DatasourceService
from ..services.llm import LLMService
from ..services.integration import IntegrationService
from ..services.task import TaskService
from ..services.user import UserService
from ..services.workflow import WorkflowService


class CodeMieClient:
    """Main client class for interacting with CodeMie API."""

    def __init__(
        self,
        auth_server_url: str,
        auth_realm_name: str,
        codemie_api_domain: str,
        auth_client_id: Optional[str] = None,
        auth_client_secret: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify_ssl: bool = True,
    ):
        """Initialize CodeMie client with authentication credentials.

        Args:
            auth_server_url: Keycloak server URL
            auth_realm_name: Realm name for authentication
            codemie_api_domain: CodeMie API domain
            auth_client_id: Client ID for authentication (optional if using username/password)
            auth_client_secret: Client secret for authentication (optional if using username/password)
            username: Username/email for password grant (optional if using client credentials)
            password: Password for password grant (optional if using client credentials)
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        self.auth = KeycloakCredentials(
            server_url=auth_server_url,
            realm_name=auth_realm_name,
            client_id=auth_client_id,
            client_secret=auth_client_secret,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
        )

        self._token: Optional[str] = None
        self._api_domain = codemie_api_domain.rstrip("/")
        self._verify_ssl = verify_ssl
        if not verify_ssl:
            import requests
            from urllib3.exceptions import InsecureRequestWarning

            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # Initialize token first
        self._token = self.auth.get_token()

        # Initialize services with verify_ssl parameter and token
        self.assistants = AssistantService(
            self._api_domain, self._token, verify_ssl=verify_ssl
        )
        self.llms = LLMService(self._api_domain, self._token, verify_ssl=verify_ssl)
        self.integrations = IntegrationService(
            self._api_domain, self._token, verify_ssl=verify_ssl
        )
        self.tasks = TaskService(self._api_domain, self._token, verify_ssl=verify_ssl)
        self.users = UserService(self._api_domain, self._token, verify_ssl=verify_ssl)
        self.datasources = DatasourceService(
            self._api_domain, self._token, verify_ssl=verify_ssl
        )
        self.workflows = WorkflowService(
            self._api_domain, self._token, verify_ssl=self._verify_ssl
        )

    @property
    def token(self) -> str:
        """Get current token or fetch new one if not available."""
        if not self._token:
            self._token = self.auth.get_token()
        return self._token

    def refresh_token(self) -> str:
        """Force token refresh."""
        self._token = self.auth.get_token()
        # Update token in services
        self.assistants = AssistantService(
            self._api_domain, self._token, verify_ssl=self._verify_ssl
        )
        self.llms = LLMService(
            self._api_domain, self._token, verify_ssl=self._verify_ssl
        )
        self.integrations = IntegrationService(
            self._api_domain, self._token, verify_ssl=self._verify_ssl
        )
        self.tasks = TaskService(
            self._api_domain, self._token, verify_ssl=self._verify_ssl
        )
        self.users = UserService(
            self._api_domain, self._token, verify_ssl=self._verify_ssl
        )
        self.datasources = DatasourceService(
            self._api_domain, self._token, verify_ssl=self._verify_ssl
        )
        self.workflows = WorkflowService(
            self._api_domain, self._token, verify_ssl=self._verify_ssl
        )
        return self._token
