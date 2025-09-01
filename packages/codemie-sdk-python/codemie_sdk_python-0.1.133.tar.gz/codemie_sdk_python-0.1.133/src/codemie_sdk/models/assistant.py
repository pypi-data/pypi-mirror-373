"""Models for assistant-related data structures."""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional, Any, Union, Dict, Type

from pydantic import BaseModel, Field, ConfigDict, model_validator

from .common import User
from .integration import Integration


class ToolDetails(BaseModel):
    """Model for tool details."""

    model_config = ConfigDict(extra="ignore")

    name: str
    label: Optional[str] = None
    settings_config: bool = False
    user_description: Optional[str] = None
    settings: Optional[Integration] = None


class ToolKitDetails(BaseModel):
    """Model for toolkit details."""

    model_config = ConfigDict(extra="ignore")

    toolkit: str
    tools: List[ToolDetails]
    label: str = ""
    settings_config: bool = False
    is_external: bool = False
    settings: Optional[Integration] = None


class ContextType(str, Enum):
    """Enum for context types."""

    KNOWLEDGE_BASE = "knowledge_base"
    CODE = "code"
    PROVIDER = "provider"


class Context(BaseModel):
    """Model for context configuration."""

    model_config = ConfigDict(extra="ignore")

    context_type: ContextType
    name: str


class MCPServerConfig(BaseModel):
    """
    Configuration for an MCP server.

    Defines how to start and connect to an MCP server instance, including
    command, arguments, environment variables, and authentication parameters.

    Attributes:
        command (str): The command used to invoke the MCP server
        args (Optional[list[str]]): List of arguments for the server command
        env (Optional[dict[str, Any]]): Environment variables for the server process
        auth_token (Optional[str]): Authentication token for MCP-Connect server
    """

    command: Optional[str] = Field(
        None,
        description="The command used to invoke the MCP server (e.g., 'npx', 'uvx') using a stdio transport",
    )
    url: Optional[str] = Field(
        None,
        description="The HTTP URL of a remote MCP server (use when connecting over HTTP/streamable-http).",
    )
    args: Optional[list[str]] = Field(
        default_factory=list,
        description="List of arguments to pass to the MCP server command",
    )
    headers: Optional[dict[str, str]] = Field(
        default_factory=dict,
        description="HTTP headers to include when connecting to an MCP server via `url`.",
    )
    env: Optional[dict[str, Any]] = Field(
        default_factory=dict,
        description="Environment variables to be set for the MCP server process",
    )
    type: Optional[str] = Field(
        None,
        description="Transport type. Set to 'streamable-http' to use a streamable HTTP transport; "
        "leave null for stdio/sse command transports.",
    )
    auth_token: Optional[str] = Field(
        None, description="Authentication token for the MCP-Connect server"
    )


class MCPServerDetails(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    description: Optional[str]
    enabled: bool
    config: Optional[MCPServerConfig] = None
    mcp_connect_url: Optional[str] = None
    tools_tokens_size_limit: Optional[int] = None
    command: Optional[str] = None
    arguments: Optional[str] = None
    settings: Optional[Integration] = None
    mcp_connect_auth_token: Optional[Integration] = None


class SystemPromptHistory(BaseModel):
    """Model for system prompt history."""

    model_config = ConfigDict(extra="ignore")

    system_prompt: str
    date: datetime
    created_by: Optional[User] = None


class AssistantBase(BaseModel):
    """Base model for assistant with common fields."""

    def __getitem__(self, key):
        return getattr(self, key)

    model_config = ConfigDict(extra="ignore")

    id: Optional[str] = None
    created_by: Optional[User] = None
    name: str
    description: str
    icon_url: Optional[str] = None


class Assistant(AssistantBase):
    """Full assistant model with additional fields."""

    model_config = ConfigDict(extra="ignore", use_enum_values=True)

    system_prompt: str
    system_prompt_history: List[SystemPromptHistory] = Field(default_factory=list)
    project: str
    llm_model_type: Optional[str] = None
    toolkits: List[ToolKitDetails] = Field(default_factory=list)
    user_prompts: List[str] = Field(default_factory=list)
    shared: bool = False
    is_react: bool = False
    is_global: bool = False
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    creator: str = "system"
    slug: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    context: List[Context] = Field(default_factory=list)
    user_abilities: Optional[List[Any]] = None
    mcp_servers: List[MCPServerDetails] = Field(default_factory=list)
    assistant_ids: List[str] = Field(default_factory=list)


class AssistantRequestBase(AssistantBase):
    """Base model for assistant requests with common request fields."""

    def __getitem__(self, key):
        return getattr(self, key)

    model_config = ConfigDict(extra="ignore", use_enum_values=True)

    system_prompt: str
    project: str
    context: List[Context] = Field(default_factory=list)
    llm_model_type: str
    toolkits: List[ToolKitDetails] = Field(default_factory=list)
    user_prompts: List[str] = Field(default_factory=list)
    shared: bool = False
    is_react: bool = False
    is_global: Optional[bool] = False
    slug: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    mcp_servers: List[MCPServerDetails] = Field(default_factory=list)
    assistant_ids: List[str] = Field(default_factory=list)


class AssistantCreateRequest(AssistantRequestBase):
    """Model for creating a new assistant."""

    pass


class AssistantUpdateRequest(AssistantRequestBase):
    """Model for updating an existing assistant."""

    pass


class ChatRole(str, Enum):
    """Enum for chat message roles."""

    ASSISTANT = "Assistant"
    USER = "User"


class ChatMessage(BaseModel):
    """Model for chat message."""

    role: ChatRole
    message: Optional[str] = Field(default="")


class ToolConfig(BaseModel):
    name: str
    tool_creds: Optional[Dict[str, Any]] = None
    integration_id: Optional[str] = None

    @model_validator(mode="after")
    def validate_credentials_provided(self) -> "ToolConfig":
        """
        Validate that either tool_creds or integration_id is provided.

        At least one of these fields must be specified for the tool configuration
        to be valid. This ensures that the tool has a way to obtain credentials.
        """
        if not self.tool_creds and not self.integration_id:
            raise ValueError("Either tool_creds or integration_id must be provided")
        if self.tool_creds and self.integration_id:
            raise ValueError(
                "Either tool_creds or integration_id must be provided, but not both"
            )
        return self


class AssistantChatRequest(BaseModel):
    """Model for chat request to assistant."""

    conversation_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Conversation identifier"
    )
    text: str = Field(description="User's input")
    content_raw: Optional[str] = Field(default="", description="Raw content input")
    file_names: List[str] = Field(
        default_factory=list, description="List of file names"
    )
    llm_model: Optional[str] = Field(
        default=None, description="Specific LLM model to use"
    )
    history: Union[List[ChatMessage], str] = Field(
        default_factory=list,
        description="Conversation history as list of messages or string",
    )
    history_index: int = Field(
        default=None, description="DataSource in conversation history"
    )
    stream: bool = Field(default=False, description="Enable streaming response")
    top_k: int = Field(default=10, description="Top K results to consider")
    system_prompt: str = Field(default="", description="Override system prompt")
    background_task: bool = Field(default=False, description="Run as background task")
    metadata: Optional[dict[str, Any]] = Field(
        default=None, description="Provide additional metadata"
    )
    tools_config: Optional[List[ToolConfig]] = None
    output_schema: Optional[dict | Type[BaseModel]] = Field(
        default=None,
        description="Structured output schema for the agent. \
            If specified, `generated` field in response will have the same type",
    )


class BaseModelResponse(BaseModel):
    """Model for chat response from assistant."""

    generated: str | dict | BaseModel = Field(
        description="Generated response. If output_schema in request is specified, corresponds with its type"
    )
    time_elapsed: Optional[float] = Field(
        default=None, alias="timeElapsed", description="Time taken for generation"
    )
    tokens_used: Optional[int] = Field(
        default=None, alias="tokensUsed", description="Number of tokens used"
    )
    thoughts: Optional[List[dict]] = Field(
        default=None, description="Thought process details"
    )
    task_id: Optional[str] = Field(
        default=None, alias="taskId", description="Background task identifier"
    )

    class Config:
        # Allow population by field name as well as alias
        populate_by_name = True
        # Preserve alias on export
        alias_generator = None


class EnvVars(BaseModel):
    azure_openai_url: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    openai_api_type: Optional[str] = None
    openai_api_version: Optional[str] = None
    models_env: Optional[str] = None


class ExportAssistantPayload(BaseModel):
    env_vars: Optional[EnvVars] = None


class AssistantEvaluationRequest(BaseModel):
    """Model for assistant evaluation request."""

    model_config = ConfigDict(extra="ignore")

    dataset_id: str = Field(description="ID of the dataset to use for evaluation")
    experiment_name: str = Field(description="Name of the evaluation experiment")
    system_prompt: Optional[str] = Field(
        default=None, description="System prompt to use for evaluation"
    )
    llm_model: Optional[str] = Field(
        default=None, description="LLM model to use for evaluation"
    )
