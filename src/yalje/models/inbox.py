"""Inbox message data model."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from yalje.models.user import InboxSender


class InboxMessage(BaseModel):
    """An inbox message from LiveJournal."""

    qid: int = Field(..., description="Queue ID from lj_qid attribute")
    msgid: Optional[int] = Field(None, description="Message ID (null for notifications)")
    type: str = Field(
        ...,
        description="Message type: user_message, system_notification, official_message",
    )
    sender: Optional[InboxSender] = Field(
        None, description="Sender information (null for system notifications)"
    )
    title: str = Field(..., description="Message title/subject")
    body: str = Field(..., description="Message content (HTML preserved)")
    timestamp_relative: str = Field(..., description="Relative timestamp (e.g., '4 months ago')")
    timestamp_absolute: Optional[str] = Field(
        None, description="Exact timestamp if available (YYYY-MM-DD HH:MM:SS)"
    )
    read: bool = Field(False, description="Read status")
    bookmarked: bool = Field(False, description="Bookmark status")

    # Pydantic v2 configuration
    model_config = ConfigDict(extra="ignore")
