"""Workflow service implementation."""

import json
from typing import List, Optional, Any, Dict

from .workflow_execution import WorkflowExecutionService
from ..models.common import PaginationParams
from ..models.workflow import (
    WorkflowCreateRequest,
    WorkflowUpdateRequest,
    Workflow,
)
from ..utils import ApiRequestHandler


class WorkflowService:
    """Service for managing CodeMie workflows."""

    def __init__(self, api_domain: str, token: str, verify_ssl: bool = True):
        """Initialize the workflow service.

        Args:
            api_domain: Base URL for the CodeMie API
            token: Authentication token
            verify_ssl: Whether to verify SSL certificates
        """
        self._api = ApiRequestHandler(api_domain, token, verify_ssl)

    def get_prebuilt(self) -> List[Workflow]:
        """Get list of prebuilt workflows.

        Returns:
            List of prebuilt workflow templates
        """
        return self._api.get("/v1/workflows/prebuilt", List[Workflow])

    def create_workflow(self, request: WorkflowCreateRequest) -> dict:
        """Create a new workflow.

        Args:
            request: The workflow creation request containing required fields:
                    - name: Name of the workflow
                    - description: Description of the workflow
                    - project: Project identifier
                    - yaml_config: YAML configuration for the workflow
                    Optional fields with defaults:
                    - mode: WorkflowMode (defaults to SEQUENTIAL)
                    - shared: bool (defaults to False)
                    - icon_url: Optional URL for workflow icon

        Returns:
            Created WorkflowTemplate instance
        """
        return self._api.post("/v1/workflows", dict, json_data=request.model_dump())

    def update(self, workflow_id: str, request: WorkflowUpdateRequest) -> dict:
        """Update an existing workflow.

        Args:
            workflow_id: ID of the workflow to update
            request: The workflow update request containing optional fields to update:
                    - name: New name for the workflow
                    - description: New description
                    - yaml_config: New YAML configuration
                    - mode: New workflow mode
                    - shared: New sharing status
                    - icon_url: New icon URL
                    Only specified fields will be updated.

        Returns:
            Updated WorkflowTemplate instance
        """
        return self._api.put(
            f"/v1/workflows/{workflow_id}",
            dict,
            json_data=request.model_dump(exclude_none=True),
        )

    def list(
        self,
        page: int = 0,
        per_page: int = 10,
        projects: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Workflow]:
        """List workflows with filtering and pagination support.

        Args:
            page: Page number (0-based). Must be >= 0. Defaults to 0.
            per_page: Number of items per page. Must be > 0. Defaults to 10.
            projects: Optional projects to filter by.
            filters: Optional filters to apply. Should be a dictionary with filter criteria.

        Returns:
            List of Workflow objects containing workflow information and pagination metadata.

        """

        params = PaginationParams(page=page, per_page=per_page).to_dict()

        if projects:
            params["project"] = projects
        if filters:
            params["filters"] = json.dumps(filters)

        return self._api.get("/v1/workflows", List[Workflow], params=params)

    def get(self, workflow_id: str) -> Workflow:
        """Get workflow by ID.

        Args:
            workflow_id: The ID of the workflow to retrieve.

        Returns:
            Workflow object containing the workflow information.

        Raises:
            ApiError: If the workflow is not found or other API errors occur.
        """
        return self._api.get(f"/v1/workflows/id/{workflow_id}", Workflow)

    def delete(self, workflow_id: str) -> dict:
        """Delete a workflow by ID.

        Args:
            workflow_id: ID of the workflow to delete

        Returns:
            Deletion confirmation
        """
        return self._api.delete(f"/v1/workflows/{workflow_id}", dict)

    def run(self, workflow_id: str, user_input: str = "") -> dict:
        return self.executions(workflow_id).create(user_input)

    def executions(self, workflow_id: str) -> WorkflowExecutionService:
        """Get workflow execution service for the specified workflow.

        Args:
            workflow_id: ID of the workflow to manage executions for

        Returns:
            WorkflowExecutionService instance configured for the specified workflow
        """
        return WorkflowExecutionService(self._api, workflow_id)
