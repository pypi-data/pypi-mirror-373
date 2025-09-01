"""Assistant service implementation."""

import json
from pathlib import Path
from typing import List, Union, Optional, Dict, Any, Literal
from pydantic import BaseModel
from copy import deepcopy

import requests
import mimetypes

from ..models.assistant import (
    Assistant,
    AssistantCreateRequest,
    AssistantUpdateRequest,
    ToolKitDetails,
    AssistantChatRequest,
    BaseModelResponse,
    AssistantBase,
    Context,
    ExportAssistantPayload,
    AssistantEvaluationRequest,
)
from ..models.common import PaginationParams
from ..utils import ApiRequestHandler


class AssistantService:
    """Service for managing CodeMie assistants."""

    def __init__(self, api_domain: str, token: str, verify_ssl: bool = True):
        """Initialize the assistant service.

        Args:
            api_domain: Base URL for the CodeMie API
            token: Authentication token
            verify_ssl: Whether to verify SSL certificates
        """
        self._api = ApiRequestHandler(api_domain, token, verify_ssl)

    def list(
        self,
        minimal_response: bool = True,
        scope: Literal["visible_to_user", "marketplace"] = "visible_to_user",
        page: int = 0,
        per_page: int = 12,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Union[Assistant, AssistantBase]]:
        """Get list of available assistants.

        Args:
            minimal_response: Whether to return minimal assistant info
            scope: Visibility scope of assistants to retrieve
            page: Page number for pagination
            per_page: Number of items per page
            filters: Optional filters to apply

        Returns:
            List of assistants matching the criteria
        """
        params = PaginationParams(page=page, per_page=per_page).to_dict()
        params["scope"] = scope
        params["minimal_response"] = minimal_response
        if filters:
            params["filters"] = json.dumps(filters)

        model = AssistantBase if minimal_response else Assistant
        return self._api.get("/v1/assistants", List[model], params=params)

    def get(self, assistant_id: str) -> Assistant:
        """Get assistant by ID.

        Args:
            assistant_id: ID of the assistant to retrieve

        Returns:
            Assistant details
        """
        return self._api.get(f"/v1/assistants/id/{assistant_id}", Assistant)

    def get_by_slug(self, slug: str) -> Assistant:
        """Get assistant by slug.

        Args:
            slug: Slug of the assistant to retrieve

        Returns:
            Assistant details
        """
        return self._api.get(f"/v1/assistants/slug/{slug}", Assistant)

    def create(self, request: AssistantCreateRequest) -> dict:
        """Create a new assistant.

        Args:
            request: Assistant creation request

        Returns:
            Created assistant details
        """
        return self._api.post(
            "/v1/assistants", dict, json_data=request.model_dump(exclude_none=True)
        )

    def update(self, assistant_id: str, request: AssistantUpdateRequest) -> dict:
        """Update an existing assistant.

        Args:
            assistant_id: ID of the assistant to update
            request: Assistant update request

        Returns:
            Updated assistant details
        """
        return self._api.put(
            f"/v1/assistants/{assistant_id}",
            dict,
            json_data=request.model_dump(exclude_none=True),
        )

    def get_tools(self) -> List[ToolKitDetails]:
        """Get list of available tools.

        Returns:
            List of available tool kits
        """
        return self._api.get(
            "/v1/assistants/tools", List[ToolKitDetails], wrap_response=False
        )

    def get_context(self, project_name: str) -> List[Context]:
        """Get list of available contexts.

        Args: project_name: Name of the project to retrieve context for

        Returns:
            All available assistants context
        """
        params = {"project_name": project_name}
        return self._api.get("/v1/assistants/context", List[Context], params=params)

    def delete(self, assistant_id: str) -> dict:
        """Delete an assistant by ID.

        Args:
            assistant_id: ID of the assistant to delete

        Returns:
            Deletion confirmation
        """
        return self._api.delete(f"/v1/assistants/{assistant_id}", dict)

    def get_prebuilt(self) -> List[Assistant]:
        """Get list of prebuilt assistants.

        Returns:
            List of prebuilt assistants
        """
        return self._api.get("/v1/assistants/prebuilt", List[Assistant])

    def get_prebuilt_by_slug(self, slug: str) -> Assistant:
        """Get prebuilt assistant by slug.

        Args:
            slug: Slug of the prebuilt assistant to retrieve

        Returns:
            Prebuilt assistant details
        """
        return self._api.get(f"/v1/assistants/prebuilt/{slug}", Assistant)

    def chat(
        self,
        assistant_id: str,
        request: AssistantChatRequest,
    ) -> Union[requests.Response, BaseModelResponse]:
        """Send a chat request to an assistant.

        Args:
            assistant_id: ID of the assistant to chat with
            request: Chat request details

        Returns:
            Chat response or streaming response
        """
        pydantic_schema = None
        if issubclass(request.output_schema, BaseModel):
            pydantic_schema = deepcopy(request.output_schema)
            request.output_schema = request.output_schema.model_json_schema()

        response = self._api.post(
            f"/v1/assistants/{assistant_id}/model",
            BaseModelResponse,
            json_data=request.model_dump(exclude_none=True, by_alias=True),
            stream=request.stream,
        )
        if not request.stream and pydantic_schema:
            # we do conversion to the BaseModel here because self._parse_response don't see actual request model,
            # where reflected desired output format for structured output
            response.generated = pydantic_schema.model_validate(response.generated)

        return response

    def upload_file_to_chat(self, file_path: Path):
        """Upload a file to assistant chat and return the response containing file_url."""

        with open(file_path, "rb") as file:
            files = [
                (
                    "file",
                    (
                        file_path.name,
                        file,
                        mimetypes.guess_type(file_path.name)[0]
                        or "application/octet-stream",
                    ),
                ),
            ]
            response = self._api.post_multipart("/v1/files/", dict, files=files)

        return response

    def export(self, assistant_id: str, request: ExportAssistantPayload):
        """Export an assistant.

        Args:
            assistant_id: ID of the assistant to export
            request: Export request details

        Returns:
             input stream of the exported assistant file"""

        return self._api.post(
            f"/v1/assistants/id/{assistant_id}/export",
            response_model=Any,
            stream=True,
            json_data=request.model_dump(exclude_none=True),
        )

    def evaluate(self, assistant_id: str, request: AssistantEvaluationRequest) -> dict:
        """Evaluate an assistant with a dataset.

        Args:
            assistant_id: ID of the assistant to evaluate
            request: Evaluation request details

        Returns:
            Evaluation results
        """
        return self._api.post(
            f"/v1/assistants/{assistant_id}/evaluate",
            dict,
            json_data=request.model_dump(exclude_none=True),
        )
