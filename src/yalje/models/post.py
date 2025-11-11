"""Blog post data model."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Post(BaseModel):
    """A LiveJournal blog post."""

    itemid: int = Field(..., description="Unique post identifier")
    jitemid: Optional[int] = Field(
        None, description="Post identifier for comment linking (relationship TBD)"
    )
    eventtime: str = Field(..., description="Publication datetime (YYYY-MM-DD HH:MM:SS)")
    logtime: str = Field(..., description="Log/save datetime (YYYY-MM-DD HH:MM:SS)")
    subject: Optional[str] = Field(None, description="Post title")
    event: str = Field(..., description="Post body content (HTML preserved)")
    security: str = Field(
        ..., description="Access level: public, private, friends, usemask, custom"
    )
    allowmask: int = Field(0, description="Bitmask for custom friend groups")
    current_mood: Optional[str] = Field(None, description="Mood metadata")
    current_music: Optional[str] = Field(None, description="Music metadata")

    @field_validator("security")
    @classmethod
    def validate_security(cls, v: str) -> str:
        """Validate security level."""
        valid_levels = {"public", "private", "friends", "usemask", "custom"}
        if v not in valid_levels:
            raise ValueError(f"security must be one of {valid_levels}")
        return v

    # Pydantic v2 configuration
    model_config = ConfigDict(
        extra="ignore",  # Allow extra fields in case LJ adds more metadata
    )
