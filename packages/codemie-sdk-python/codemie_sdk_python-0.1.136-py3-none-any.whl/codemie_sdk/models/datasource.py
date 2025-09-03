import re
from datetime import datetime
from enum import Enum
from typing import Optional, List, Union, Tuple

from pydantic import BaseModel, Field, model_validator, ConfigDict, field_validator

from .common import TokensUsage, User


class CodeDataSourceType(str, Enum):
    CODE = "code"
    SUMMARY = "summary"
    CHUNK_SUMMARY = "chunk-summary"


class DataSourceType(str, Enum):
    CODE = "code"
    CONFLUENCE = "knowledge_base_confluence"
    JIRA = "knowledge_base_jira"
    FILE = "knowledge_base_file"
    GOOGLE = "llm_routing_google"
    PROVIDER = "provider"
    SUMMARY = "summary"
    CHUNK_SUMMARY = "chunk-summary"
    JSON = "knowledge_base_json"
    BEDROCK = "knowledge_base_bedrock"


class DataSourceStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    FETCHING = "fetching"
    IN_PROGRESS = "in_progress"


class DataSourceProcessingInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    total_documents_count: Optional[int] = Field(None, alias="total_documents")
    skipped_documents_count: Optional[int] = Field(None, alias="skipped_documents")
    total_size_kb: Optional[float] = None
    average_file_size_bytes: Optional[float] = None
    unique_extensions: Optional[List[str]] = None
    filtered_documents: Optional[Union[int, list]] = None
    processed_documents_count: Optional[int] = Field(None, alias="documents_count_key")


# Base request models
class Confluence(BaseModel):
    """Model for Confluence-specific response fields"""

    cql: Optional[str] = None
    include_restricted_content: Optional[bool] = None
    include_archived_content: Optional[bool] = None
    include_attachments: Optional[bool] = None
    include_comments: Optional[bool] = None
    keep_markdown_format: Optional[bool] = None
    keep_newlines: Optional[bool] = None
    max_pages: Optional[int] = None
    pages_per_request: Optional[int] = None

    model_config = ConfigDict(extra="ignore")


class Jira(BaseModel):
    """Model for Jira-specific response fields"""

    jql: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class Google(BaseModel):
    """Model for Google-specific response fields"""

    google_doc: str = Field(None, alias="googleDoc")

    model_config = ConfigDict(extra="ignore")


class File(BaseModel):
    """Model for File-specific response fields"""

    files: Optional[List[Tuple[str, bytes, str]]] = (
        None  # (filename, content, mime_type)
    )

    model_config = ConfigDict(extra="ignore")


class Code(BaseModel):
    """Model for code repository datasource creation"""

    link: Optional[str] = Field(..., min_length=1, max_length=1000)
    branch: Optional[str] = Field(..., min_length=1, max_length=1000)
    index_type: Optional[CodeDataSourceType] = Field(None, alias="indexType")
    files_filter: Optional[str] = Field(default="", alias="filesFilter")
    embeddings_model: Optional[str] = Field(None, alias="embeddingsModel")
    summarization_model: Optional[str] = Field(None, alias="summarizationModel")
    prompt: Optional[str] = None
    docs_generation: bool = Field(False, alias="docsGeneration")


class BaseDataSourceRequest(BaseModel):
    """Base model for all datasource creation requests"""

    name: str = Field(
        ...,
        description="Name must contain only lowercase letters and underscores.",
        max_length=50,
    )
    project_name: str
    description: str = Field(..., max_length=100)
    shared_with_project: bool = Field(False, alias="project_space_visible")
    setting_id: str = Field(None)
    type: DataSourceType

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    @classmethod
    def required_fields(cls) -> List[str]:
        return []

    @field_validator("name")
    def validate_name_field(cls, value):
        if not re.fullmatch(r"^[a-z][a-z_-]*$", value):
            raise ValueError(
                "Name must contain only lowercase letters and underscores, and cannot begin with '_' or '-'."
            )
        return value

    @model_validator(mode="before")
    def pre_init_validator(cls, values):
        # Ensure that at least one of the fields is not None
        if cls.required_fields() and not any(
            values.get(field) for field in cls.required_fields()
        ):
            raise ValueError(
                f"At least one of the following fields must be set: {', '.join(cls.required_fields())}"
            )
        return values


class CodeDataSourceRequest(BaseDataSourceRequest, Code):
    # Override to comply with keys in json
    project_space_visible: bool = Field(False, alias="projectSpaceVisible")
    setting_id: str = Field(None, alias="settingId")

    def __init__(self, **data):
        super().__init__(type=DataSourceType.CODE, **data)

    @classmethod
    def required_fields(cls) -> List[str]:
        return ["link", "embeddings_model", "branch", "index_type"]


class JiraDataSourceRequest(BaseDataSourceRequest, Jira):
    def __init__(self, **data):
        super().__init__(type=DataSourceType.JIRA, **data)

    @classmethod
    def required_fields(cls) -> List[str]:
        return ["jql"]


class ConfluenceDataSourceRequest(BaseDataSourceRequest, Confluence):
    def __init__(self, **data):
        super().__init__(type=DataSourceType.CONFLUENCE, **data)

    @classmethod
    def required_fields(cls) -> List[str]:
        return ["cql"]


class GoogleDataSourceRequest(BaseDataSourceRequest, Google):
    def __init__(self, **data):
        super().__init__(type=DataSourceType.GOOGLE, **data)

    @classmethod
    def required_fields(cls) -> List[str]:
        return ["google_doc"]


class FileDataSourceRequest(BaseDataSourceRequest):
    """Model for File datasource creation requests"""

    def __init__(self, **data):
        super().__init__(type=DataSourceType.FILE, **data)


class BaseUpdateDataSourceRequest(BaseDataSourceRequest):
    """Mixin update-specific reindex fields"""

    full_reindex: Optional[bool] = Field(None)
    skip_reindex: Optional[bool] = Field(None)
    resume_indexing: Optional[bool] = Field(None)
    incremental_reindex: Optional[bool] = Field(None)

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    @model_validator(mode="after")
    def validate_reindex_options(self) -> "BaseUpdateDataSourceRequest":
        ds_type = self.type

        if ds_type == DataSourceType.CONFLUENCE:
            if self.incremental_reindex:
                raise ValueError(
                    "Confluence data sources only support full_reindex and resume_indexing"
                )

        elif ds_type == DataSourceType.JIRA:
            if self.resume_indexing:
                raise ValueError(
                    "Jira data sources only support full_reindex and incremental_reindex"
                )

        elif ds_type == DataSourceType.CODE:
            if self.incremental_reindex:
                raise ValueError("Code data sources do not support incremental_reindex")

        elif ds_type == DataSourceType.GOOGLE:
            if self.resume_indexing or self.incremental_reindex:
                raise ValueError("Google data sources only support full_reindex")

        return self


class UpdateCodeDataSourceRequest(BaseUpdateDataSourceRequest, Code):
    """Model for code repository datasource updates"""

    def __init__(self, **data):
        super().__init__(type=DataSourceType.CODE, **data)


class UpdateConfluenceDataSourceRequest(BaseUpdateDataSourceRequest, Confluence):
    def __init__(self, **data):
        super().__init__(type=DataSourceType.CONFLUENCE, **data)


class UpdateJiraDataSourceRequest(BaseUpdateDataSourceRequest, Jira):
    def __init__(self, **data):
        super().__init__(type=DataSourceType.JIRA, **data)


class UpdateGoogleDataSourceRequest(BaseUpdateDataSourceRequest):
    """Model for Google docs datasource updates"""

    google_doc: Optional[str] = Field(None, alias="googleDoc")

    def __init__(self, **data):
        super().__init__(type=DataSourceType.GOOGLE, **data)


class UpdateFileDataSourceRequest(BaseUpdateDataSourceRequest):
    """Model for File datasource updates"""

    def __init__(self, **data):
        super().__init__(type=DataSourceType.FILE, **data)


class DataSource(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
    )

    def __getitem__(self, key):
        return getattr(self, key)

    id: str
    project_name: str
    name: str = Field(None, alias="repo_name")
    description: Optional[str] = Field(None)
    type: DataSourceType = Field(None, alias="index_type")
    embeddings_model: Optional[str] = Field(None)
    status: DataSourceStatus
    setting_id: Optional[str] = Field(None)
    created_date: datetime = Field(None, alias="date")
    created_by: User
    shared_with_project: bool = Field(None, alias="project_space_visible")
    update_date: datetime
    error_message: Optional[str] = Field(None, alias="text")
    user_abilities: List[str]
    processing_info: Optional[DataSourceProcessingInfo] = Field(None)
    processed_documents: Optional[List[str]] = Field(None, alias="processed_files")
    tokens_usage: Optional[TokensUsage] = Field(None)
    # Code specific fields
    code: Optional[Code] = None
    # Jira specific fields
    jira: Optional[Jira] = None
    # Confluence specific fields
    confluence: Optional[Confluence] = None
    # Google doc specific fields
    google_doc_link: Optional[str] = None

    @model_validator(mode="before")
    def before_init(cls, values):
        if values.get("error"):
            values["status"] = DataSourceStatus.FAILED
        elif values.get("completed"):
            values["status"] = DataSourceStatus.COMPLETED
        elif values.get("is_fetching"):
            values["status"] = DataSourceStatus.FETCHING
        else:
            values["status"] = DataSourceStatus.IN_PROGRESS

        if values.get("index_type") in [
            DataSourceType.CONFLUENCE,
            DataSourceType.JIRA,
            DataSourceType.GOOGLE,
        ]:
            complete_state = values.get("complete_state", 0)
            if complete_state is not None:
                values["processing_info"] = {"documents_count_key": complete_state}
        elif values.get("index_type") == DataSourceType.CODE:
            values["code"] = {
                "link": values.get("link"),
                "branch": values.get("branch"),
                "files_filter": values.get("files_filter"),
                "summarization_prompt": values.get("prompt"),
                "summarization_model": values.get("summarization_model"),
                "summarization_docs_generation": values.get("docs_generation"),
                "embeddings_model": values.get("embeddings_model"),
            }
        return values
