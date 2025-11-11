"""Comment data model."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Comment(BaseModel):
    """A comment on a LiveJournal post."""

    id: int = Field(..., description="Unique comment ID")
    jitemid: int = Field(..., description="Post identifier (links to post via jitemid)")
    posterid: Optional[int] = Field(None, description="User ID (null = anonymous)")
    poster_username: Optional[str] = Field(None, description="Username resolved from usermap")
    parentid: Optional[int] = Field(None, description="Parent comment ID (null = top-level)")
    date: str = Field(..., description="Comment timestamp (YYYY-MM-DD HH:MM:SS)")
    subject: Optional[str] = Field(None, description="Comment subject/title")
    body: Optional[str] = Field(None, description="Comment content (HTML preserved)")
    state: Optional[str] = Field(None, description="'deleted' or null")

    # Pydantic v2 configuration
    model_config = ConfigDict(extra="ignore")
