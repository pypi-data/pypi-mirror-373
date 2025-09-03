"""Integration service implementation."""

import json
from typing import List, Optional, Dict, Any

from ..exceptions import NotFoundError
from ..models.common import PaginationParams
from ..models.integration import (
    Integration,
    IntegrationType,
    IntegrationTestRequest,
)
from ..utils import ApiRequestHandler


class IntegrationService:
    """Service for managing CodeMie integrations (both user and project settings)."""

    def __init__(self, api_domain: str, token: str, verify_ssl: bool = True):
        """Initialize the integration service.

        Args:
            api_domain: Base URL for the CodeMie API
            token: Authentication token
            verify_ssl: Whether to verify SSL certificates
        """
        self._api = ApiRequestHandler(api_domain, token, verify_ssl)

    def _get_base_path(self, setting_type: IntegrationType) -> str:
        """Get base API path based on setting type.

        Args:
            setting_type: Type of settings (USER or PROJECT)

        Returns:
            Base API path for the specified setting type
        """
        return f"/v1/settings/{'user' if setting_type == IntegrationType.USER else 'project'}"

    def list(
        self,
        setting_type: IntegrationType = IntegrationType.USER,
        page: int = 0,
        per_page: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Integration]:
        """Get list of available integrations.

        Args:
            setting_type: Type of settings to list (USER or PROJECT)
            page: Page number for pagination
            per_page: Number of items per page
            filters: Optional filters to apply

        Returns:
            List of integrations matching the criteria
        """
        params = PaginationParams(page=page, per_page=per_page).to_dict()
        if filters:
            params["filters"] = json.dumps(filters)

        return self._api.get(
            self._get_base_path(setting_type), List[Integration], params=params
        )

    def get(
        self, integration_id: str, setting_type: IntegrationType = IntegrationType.USER
    ) -> Integration:
        """Get integration by ID.

        Args:
            integration_id: ID of the integration to retrieve
            setting_type: Type of settings to get (USER or PROJECT)

        Returns:
            Integration details

        Raises:
            NotFoundError: If integration with given ID is not found
        """
        integrations = self.list(setting_type=setting_type, per_page=100)
        integration = next((i for i in integrations if i.id == integration_id), None)
        if integration is None:
            raise NotFoundError("Integration", integration_id)

        return integration

    def get_by_alias(
        self, alias: str, setting_type: IntegrationType = IntegrationType.USER
    ) -> Optional[Integration]:
        """Get integration by its alias.

        Args:
            alias: Alias of the integration to retrieve
            setting_type: Type of settings to get (USER or PROJECT)

        Returns:
            Integration details if found, None otherwise

        Raises:
            NotFoundError: If integration with given alias is not found
        """
        integrations = self.list(setting_type=setting_type, per_page=100)
        integration = next((i for i in integrations if i.alias == alias), None)

        if integration is None:
            raise NotFoundError("Integration", alias)

        return integration

    def create(self, settings: Integration) -> dict:
        """Create a new integration.

        Args:
            settings: integration creation request

        Returns:
            Created integration details
        """
        return self._api.post(
            self._get_base_path(settings.setting_type),
            dict,
            json_data=settings.model_dump(exclude_none=True),
        )

    def update(self, setting_id: str, settings: Integration) -> dict:
        """Update an existing integration.

        Args:
            setting_id: ID of the integration to update
            settings: integration update request

        Returns:
            Updated integration details
        """
        return self._api.put(
            f"{self._get_base_path(settings.setting_type)}/{setting_id}",
            dict,
            json_data=settings.model_dump(exclude_none=True),
        )

    def delete(
        self, setting_id: str, setting_type: IntegrationType = IntegrationType.USER
    ) -> dict:
        """Delete an integration by ID.

        Args:
            setting_id: ID of the integration to delete
            setting_type: Type of settings to delete (USER or PROJECT)

        Returns:
            Deletion confirmation
        """
        return self._api.delete(
            f"{self._get_base_path(setting_type)}/{setting_id}", dict
        )

    def test(self, integration: IntegrationTestRequest, response_type: Any) -> Any:
        """Test an integration.

        Args:
            integration: IntegrationTestRequest - integration to test
            response_type: Type of response expected

        Returns:
            Test integration response
        """
        return self._api.post(
            "/v1/settings/test/",
            response_model=response_type,
            json_data=integration.model_dump(exclude_none=True),
        )
