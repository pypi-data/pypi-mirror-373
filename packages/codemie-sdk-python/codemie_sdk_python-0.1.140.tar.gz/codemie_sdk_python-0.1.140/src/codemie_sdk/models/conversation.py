"""Models for conversation-related data structures."""

from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from codemie_sdk.models.assistant import ContextType


class Conversation(BaseModel):
    """
    Model for conversation summary data as returned from the list endpoint.
    """

    id: str
    name: str
    folder: Optional[str]
    pinned: bool
    date: str
    assistant_ids: List[str]
    initial_assistant_id: Optional[str]


class Mark(BaseModel):
    """Model for conversation review/mark data."""

    mark: str
    rating: int
    comments: str
    date: datetime
    operator: Optional["Operator"] = None


class Operator(BaseModel):
    """Represents an operator involved in marking a conversation."""

    user_id: str
    name: str


class Thought(BaseModel):
    """Model for reasoning or tool-invocation within a message's history."""

    id: str
    parent_id: Optional[str]
    metadata: dict
    in_progress: bool
    input_text: Optional[str]
    message: Optional[str]
    author_type: str
    author_name: str
    output_format: str
    error: Optional[bool]
    children: List[str]


class HistoryMark(BaseModel):
    """Model for conversation history review/mark data."""

    mark: str
    rating: int
    comments: Optional[str]
    date: datetime


class HistoryItem(BaseModel):
    """Represents an individual message within a conversation's history."""

    role: str
    message: str
    historyIndex: int
    date: datetime
    responseTime: Optional[float]
    inputTokens: Optional[int]
    outputTokens: Optional[int]
    moneySpent: Optional[float]
    userMark: Optional[HistoryMark]
    operatorMark: Optional[HistoryMark]
    messageRaw: Optional[str]
    fileNames: List[str]
    assistantId: Optional[str]
    thoughts: Optional[List[Thought]] = Field(default_factory=list)


class ContextItem(BaseModel):
    """Represents contextual settings for conversation."""

    context_type: Optional[ContextType]
    name: str


class ToolItem(BaseModel):
    """Represents a tool used by an assistant, including configuration and description."""

    name: str
    label: Optional[str]
    settings_config: Optional[bool]
    user_description: Optional[str]


class AssistantDataItem(BaseModel):
    """Model represents details for an assistant included in a conversation."""

    assistant_id: str
    assistant_name: str
    assistant_icon: str
    assistant_type: str
    context: List[Union[ContextItem, str]]
    tools: List[ToolItem]
    conversation_starters: List[str]


class ConversationDetailsData(BaseModel):
    """Extended details about a conversation's configuration and context."""

    llm_model: Optional[str]
    context: List[ContextItem]
    app_name: Optional[str]
    repo_name: Optional[str]
    index_type: Optional[str]


class AssistantDetailsData(BaseModel):
    """Extended details about an assistant included in a conversation."""

    assistant_id: str
    assistant_name: str
    assistant_icon: str
    assistant_type: str
    context: List[Union[ContextItem, str]]
    tools: List[ToolItem]
    conversation_starters: List[str]


class ConversationDetails(BaseModel):
    """Summary information for a user conversation as returned from list endpoints."""

    id: str
    date: datetime
    update_date: datetime
    conversation_id: str
    conversation_name: str
    llm_model: Optional[str]
    folder: Optional[str]
    pinned: bool
    history: List[HistoryItem]
    user_id: str
    user_name: str
    assistant_ids: List[str]
    assistant_data: List[AssistantDataItem]
    initial_assistant_id: str
    final_user_mark: Optional[Mark]
    final_operator_mark: Optional[Mark]
    project: str
    conversation_details: Optional[ConversationDetailsData]
    assistant_details: Optional[AssistantDetailsData]
    user_abilities: Optional[List[str]]
    is_folder_migrated: bool
    category: Optional[str]
