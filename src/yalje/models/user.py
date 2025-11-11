"""User-related data models."""

from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    """User mapping from comment metadata."""

    userid: int = Field(..., description="Numeric user ID")
    username: str = Field(..., description="LiveJournal username")


class InboxSender(BaseModel):
    """Sender information for inbox messages."""

    username: str = Field(..., description="LJ username")
    display_name: str = Field(..., description="Display name")
    profile_url: str = Field(..., description="Profile URL")
    userpic_url: Optional[str] = Field(None, description="User picture URL")
    verified: bool = Field(False, description="Verified badge status")
