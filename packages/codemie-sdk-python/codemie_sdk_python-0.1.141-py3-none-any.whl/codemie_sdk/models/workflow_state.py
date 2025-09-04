"""Workflow execution state models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class WorkflowExecutionStatusEnum(str, Enum):
    """Workflow execution state status."""

    IN_PROGRESS = "In Progress"
    NOT_STARTED = "Not Started"
    INTERRUPTED = "Interrupted"
    FAILED = "Failed"
    SUCCEEDED = "Succeeded"
    ABORTED = "Aborted"


class WorkflowExecutionStateThought(BaseModel):
    """Model for workflow execution state thought."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    text: str
    created_at: datetime
    parent_id: Optional[str] = None


class WorkflowExecutionState(BaseModel):
    """Model for workflow execution state."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    execution_id: str
    name: str
    task: Optional[str] = ""
    status: WorkflowExecutionStatusEnum = WorkflowExecutionStatusEnum.NOT_STARTED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkflowExecutionStateOutput(BaseModel):
    """Model for workflow execution state output."""

    model_config = ConfigDict(populate_by_name=True)

    output: Optional[str] = None
