"""Models for user-related data structures."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    """Model representing a user profile."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    user_id: str = Field(
        description="Unique identifier of the user", validation_alias="userId"
    )
    name: str = Field(description="Full name of the user")
    username: str = Field(description="Username for authentication")
    is_admin: bool = Field(
        description="Whether the user has admin privileges", validation_alias="isAdmin"
    )
    applications: List[str] = Field(
        default_factory=list, description="List of applications the user has access to"
    )
    applications_admin: List[str] = Field(
        default_factory=list,
        description="List of applications where user has admin rights",
        validation_alias="applicationsAdmin",
    )
    picture: str = Field(default="", description="URL to user's profile picture")
    knowledge_bases: List[str] = Field(
        default_factory=list,
        description="List of knowledge bases the user has access to",
        validation_alias="knowledgeBases",
    )


class UserData(BaseModel):
    """Model representing user data."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: Optional[str] = Field(
        default=None, description="Unique identifier of the user data record"
    )
    date: Optional[str] = Field(default=None, description="Creation timestamp")
    update_date: Optional[str] = Field(
        default=None, description="Last update timestamp"
    )
    user_id: Optional[str] = Field(
        default=None, description="Associated user identifier"
    )
