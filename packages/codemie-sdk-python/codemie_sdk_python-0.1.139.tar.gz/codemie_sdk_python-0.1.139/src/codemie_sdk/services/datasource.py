"""DataSource service implementation."""

import json
import mimetypes
from typing import Literal, List, Union, Tuple, Optional, Dict, Any
from pathlib import Path

from ..models.common import PaginationParams
from ..models.datasource import (
    DataSource,
    DataSourceType,
    DataSourceStatus,
    BaseDataSourceRequest,
    CodeDataSourceRequest,
    UpdateCodeDataSourceRequest,
    BaseUpdateDataSourceRequest,
    FileDataSourceRequest,
)
from ..utils import ApiRequestHandler


class DatasourceService:
    """Service for managing CodeMie Datasources."""

    def __init__(self, api_domain: str, token: str, verify_ssl: bool = True):
        """Initialize the datasource service.

        Args:
            api_domain: Base URL for the CodeMie API
            token: Authentication token
            verify_ssl: Whether to verify SSL certificates
        """
        self._api = ApiRequestHandler(api_domain, token, verify_ssl)

    def create(self, request: BaseDataSourceRequest) -> dict:
        """Create a new datasource.

        Args:
            request: Create datasource request

        Returns:
            dict: Response from the server containing operation status
        """
        if isinstance(request, CodeDataSourceRequest):
            endpoint = f"/v1/application/{request.project_name}/index"
        else:
            # All other datasources follow the same pattern
            endpoint = f"/v1/index/knowledge_base/{request.type.name.lower()}"

        return self._api.post(
            endpoint,
            dict,
            json_data=request.model_dump(by_alias=True, exclude_none=True),
        )

    def create_file_datasource(
        self,
        request: FileDataSourceRequest,
        files: List[Union[str, Tuple[str, bytes, str]]],
    ) -> dict:
        """Create a new file datasource with file uploads.

        Args:
            request: File datasource creation request
            files: List of files to upload. Each item can be:
                   - str: file path (will read file and detect MIME type)
                   - Tuple[str, bytes, str]: (filename, content, mime_type)

        Returns:
            dict: Response from the server containing operation status
        """
        endpoint = "/v1/index/knowledge_base/file"

        # Prepare multipart form data
        params = request.model_dump(by_alias=True, exclude_none=True)
        file_uploads = []

        for file_item in files:
            if isinstance(file_item, str):
                # File path provided - read file and detect MIME type
                file_path = Path(file_item)
                with open(file_path, "rb") as f:
                    content = f.read()

                # Basic MIME type detection
                mime_type = (
                    mimetypes.guess_type(file_path.name)[0]
                    or "application/octet-stream"
                )
                file_uploads.append(("files", (file_path.name, content, mime_type)))

            elif isinstance(file_item, tuple) and len(file_item) == 3:
                # (filename, content, mime_type) tuple provided
                filename, content, mime_type = file_item
                file_uploads.append(("files", (filename, content, mime_type)))

            else:
                raise ValueError(
                    "Each file must be either a file path (str) or a tuple of (filename, content, mime_type)"
                )

        return self._api.post_multipart(
            endpoint, dict, params=params, files=file_uploads
        )

    def update(self, datasource_id: str, request: BaseUpdateDataSourceRequest) -> dict:
        """Update an existing datasource.

        Args:
            request: Update datasource request

        Returns:
            dict: Response from the server containing operation status
        """
        if isinstance(request, UpdateCodeDataSourceRequest):
            endpoint = f"/v1/application/{request.project_name}/index/{request.name}"
        else:
            endpoint = f"/v1/index/knowledge_base/{request.type.name.lower()}"

        # Extract reindex params
        params = {
            "full_reindex": request.full_reindex,
            "skip_reindex": request.skip_reindex,
            "resume_indexing": request.resume_indexing,
            "incremental_reindex": request.incremental_reindex,
        }

        # Remove reindex fields from request body
        data = request.model_dump(by_alias=True, exclude_none=True)
        for param in params.keys():
            data.pop(param, None)

        return self._api.put(endpoint, dict, params=params, json_data=data)

    def list(
        self,
        page: int = 0,
        per_page: int = 10,
        sort_key: Literal["date", "update_date"] = "update_date",
        sort_order: Literal["asc", "desc"] = "desc",
        datasource_types: List[DataSourceType] = None,
        projects: List[str] = None,
        owner: str = None,
        status: DataSourceStatus = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[DataSource]:
        """
        List datasources with pagination and sorting support.

        Args:
            page: Page number (0-based). Defaults to 0.
            per_page: Number of items per page. Defaults to 10.
            sort_key: Field to sort by. Either "date" or "update_date". Defaults to "update_date".
            sort_order: Sort order. Either "asc" or "desc". Defaults to "desc".
            datasource_types: Optional data source types to filter by.
            projects: Optional projects to filter by.
            owner: Optional owner to filter by in format: FirstName LastName.
            status: Optional data source status to filter by.
            filters: Optional filters to apply. Should be a dictionary with filter criteria.

        Returns:
            DataSourceListResponse object containing list of datasources and pagination information.
        """
        params = PaginationParams(page=page, per_page=per_page).to_dict()
        params["sort_key"] = sort_key
        params["sort_order"] = sort_order

        unified_filters = {}
        if datasource_types:
            unified_filters["index_type"] = datasource_types
        if projects:
            unified_filters["project"] = projects
        if status:
            unified_filters["status"] = status.value
        if owner:
            unified_filters["created_by"] = owner
        if filters:
            unified_filters.update(filters)
        if unified_filters:
            params["filters"] = json.dumps(unified_filters)

        return self._api.get("/v1/index", List[DataSource], params=params)

    def get(self, datasource_id: str) -> DataSource:
        """
        Get datasource by ID.

        Args:
            datasource_id: The ID of the datasource to retrieve.

        Returns:
            DataSource object containing the datasource information.

        Raises:
            ApiError: If the datasource is not found or other API errors occur.
        """
        return self._api.get(f"/v1/index/{datasource_id}", DataSource)

    def delete(self, datasource_id: str) -> dict:
        """Delete an datasource by ID.

        Args:
            datasource_id: ID of the datasource to delete

        Returns:
            Deletion confirmation
        """
        return self._api.delete(f"/v1/index/{datasource_id}", dict)
