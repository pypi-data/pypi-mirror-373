"""Workflow models."""

from datetime import datetime
from enum import StrEnum, Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from codemie_sdk.models.common import User, TokensUsage


class WorkflowMode(StrEnum):
    """Available workflow modes."""

    SEQUENTIAL = "Sequential"
    AUTONOMOUS = "Autonomous"


class WorkflowCreateRequest(BaseModel):
    """Request model for workflow creation."""

    model_config = ConfigDict(populate_by_name=True)

    project: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    yaml_config: str = Field(..., min_length=1)
    mode: WorkflowMode = WorkflowMode.SEQUENTIAL
    shared: bool = False
    icon_url: Optional[str] = None


class WorkflowUpdateRequest(BaseModel):
    """Request model for workflow updates."""

    model_config = ConfigDict(populate_by_name=True)
    project: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    yaml_config: str = Field(..., min_length=1)
    mode: Optional[WorkflowMode] = None
    shared: Optional[bool] = None
    icon_url: Optional[str] = None


class Workflow(BaseModel):
    """Workflow template model."""

    def __getitem__(self, key):
        return getattr(self, key)

    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = None
    project: str
    name: str
    description: Optional[str] = None
    yaml_config: Optional[str] = None
    mode: WorkflowMode = WorkflowMode.SEQUENTIAL
    shared: bool = False
    icon_url: Optional[str] = None
    created_date: Optional[datetime] = Field(None, alias="date")
    update_date: Optional[datetime] = Field(None)
    created_by: Optional[User] = None


class ExecutionStatus(str, Enum):
    IN_PROGRESS = "In Progress"
    NOT_STARTED = "Not Started"
    INTERRUPTED = "Interrupted"
    FAILED = "Failed"
    SUCCEEDED = "Succeeded"
    ABORTED = "Aborted"


class WorkflowExecution(BaseModel):
    """Model representing a workflow execution."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    execution_id: str
    workflow_id: str
    status: ExecutionStatus = Field(alias="overall_status")
    created_date: datetime = Field(alias="date")
    prompt: str
    updated_date: Optional[datetime] = Field(alias="update_date")
    created_by: User
    tokens_usage: Optional[TokensUsage] = None
