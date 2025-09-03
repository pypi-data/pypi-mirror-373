"""Models for assistant-related data structures."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Any

from pydantic import BaseModel, Field, ConfigDict, field_serializer


class CredentialTypes(str, Enum):
    """Enum for credential types."""

    JIRA = "Jira"
    CONFLUENCE = "Confluence"
    GIT = "Git"
    KUBERNETES = "Kubernetes"
    AWS = "AWS"
    GCP = "GCP"
    KEYCLOAK = "Keycloak"
    AZURE = "Azure"
    ELASTIC = "Elastic"
    OPENAPI = "OpenAPI"
    PLUGIN = "Plugin"
    FILESYSTEM = "FileSystem"
    SCHEDULER = "Scheduler"
    WEBHOOK = "Webhook"
    EMAIL = "Email"
    AZURE_DEVOPS = "AzureDevOps"
    SONAR = "Sonar"
    SQL = "SQL"
    TELEGRAM = "Telegram"
    ZEPHYR_CLOUD = "ZephyrCloud"
    ZEPHYR_SQUAD = "ZephyrSquad"
    SERVICE_NOW = "ServiceNow"
    DIAL = "DIAL"
    A2A = "A2A"
    MCP = "MCP"
    LITE_LLM = "LiteLLM"


class IntegrationType(str, Enum):
    """Enum for setting types."""

    USER = "user"
    PROJECT = "project"


class CredentialValues(BaseModel):
    """Model for credential values."""

    model_config = ConfigDict(extra="ignore")

    key: str
    value: Any


class Integration(BaseModel):
    """Model for settings configuration."""

    def __getitem__(self, key):
        return getattr(self, key)

    model_config = ConfigDict(extra="ignore")

    id: Optional[str] = None
    date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    user_id: Optional[str] = None
    project_name: str
    alias: Optional[str] = None
    default: bool = False
    is_global: bool = False
    credential_type: CredentialTypes
    credential_values: List[CredentialValues]
    setting_type: IntegrationType = Field(default=IntegrationType.USER)

    @field_serializer("date", "update_date")
    def serialize_dt(self, dt: datetime, _info):
        return dt.isoformat()


class IntegrationTestRequest(BaseModel):
    """Model for integration test request."""

    credential_type: str
    credential_values: Optional[List[CredentialValues]] = None
    setting_id: Optional[str] = None


class IntegrationTestResponse(BaseModel):
    """Model for integration test response."""

    def __getitem__(self, key):
        return getattr(self, key)

    message: str
    success: bool
