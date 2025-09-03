"""Workflow execution service implementation."""

from typing import List, Optional

from ..models.common import PaginationParams
from ..models.workflow import WorkflowExecution
from .workflow_execution_state import WorkflowExecutionStateService
from ..utils import ApiRequestHandler


class WorkflowExecutionService:
    """Service for managing workflow executions."""

    def __init__(self, api: ApiRequestHandler, workflow_id: str):
        """Initialize the workflow execution service.

        Args:
            api: Request handler for API
            workflow_id: ID of the workflow this service manages executions for
        """
        self._api = api
        self._workflow_id = workflow_id

    def list(
        self,
        page: int = 0,
        per_page: int = 10,
    ) -> List[WorkflowExecution]:
        """List executions for the workflow with filtering and pagination support.

        Args:
            page: Page number (0-based). Must be >= 0. Defaults to 0.
            per_page: Number of items per page. Must be > 0. Defaults to 10.

        Returns:
            List of WorkflowExecutions  containing execution information.
        """

        params = PaginationParams(page=page, per_page=per_page).to_dict()
        return self._api.get(
            f"/v1/workflows/{self._workflow_id}/executions",
            List[WorkflowExecution],
            params=params,
        )

    def create(self, user_input: Optional[str] = "") -> dict:
        """Create a new workflow execution.

        Args:
            user_input: Optional input data for the workflow execution.
                       Defaults to None.

        Returns:
            dict: Created workflow execution details
        """
        payload = {"user_input": user_input}
        return self._api.post(
            f"/v1/workflows/{self._workflow_id}/executions", dict, json_data=payload
        )

    def get(self, execution_id: str) -> WorkflowExecution:
        """Get workflow execution by ID.

        Args:
            execution_id: ID of the execution to retrieve

        Returns:
            dict: Workflow execution details
        """
        return self._api.get(
            f"/v1/workflows/{self._workflow_id}/executions/{execution_id}",
            WorkflowExecution,
        )

    def states(self, execution_id: str) -> WorkflowExecutionStateService:
        """Get states service for a specific workflow execution.

        Args:
            execution_id: ID of the execution to get states for

        Returns:
            WorkflowExecutionStateService: Service for managing states of this execution
        """
        return WorkflowExecutionStateService(self._api, self._workflow_id, execution_id)

    def delete_all(self) -> dict:
        """Delete all workflow executions."""
        return self._api.delete(f"/v1/workflows/{self._workflow_id}/executions", dict)

    def abort(self, execution_id: str) -> dict:
        """Abort a running workflow execution.

        Args:
            execution_id: ID of the execution to abort

        Returns:
            dict: Updated workflow execution details
        """
        return self._api.put(
            f"/v1/workflows/{self._workflow_id}/executions/{execution_id}/abort", dict
        )

    def resume(self, execution_id: str) -> dict:
        """Resume an interrupted workflow execution.

        Args:
            execution_id: ID of the execution to resume

        Returns:
            dict: Updated workflow execution details
        """
        return self._api.put(
            f"/v1/workflows/{self._workflow_id}/executions/{execution_id}/resume", dict
        )
