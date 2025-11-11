"""Blog post data model."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Post(BaseModel):
    """A LiveJournal blog post."""

    itemid: int = Field(..., description="Unique post identifier")
    jitemid: Optional[int] = Field(None, description="Calculated: itemid >> 8 (for comment linking)")
    eventtime: str = Field(..., description="Publication datetime (YYYY-MM-DD HH:MM:SS)")
    logtime: str = Field(..., description="Log/save datetime (YYYY-MM-DD HH:MM:SS)")
    subject: Optional[str] = Field(None, description="Post title")
    event: str = Field(..., description="Post body content (HTML preserved)")
    security: str = Field(..., description="Access level: public, private, friends, custom")
    allowmask: int = Field(0, description="Bitmask for custom friend groups")
    current_mood: Optional[str] = Field(None, description="Mood metadata")
    current_music: Optional[str] = Field(None, description="Music metadata")

    @model_validator(mode="after")
    def calculate_jitemid(self) -> "Post":
        """Calculate jitemid from itemid if not provided."""
        if self.jitemid is None:
            self.jitemid = self.itemid >> 8
        return self

    @field_validator("security")
    @classmethod
    def validate_security(cls, v: str) -> str:
        """Validate security level."""
        valid_levels = {"public", "private", "friends", "custom"}
        if v not in valid_levels:
            raise ValueError(f"security must be one of {valid_levels}")
        return v

    # Pydantic v2 configuration
    model_config = ConfigDict(
        extra="ignore",  # Allow extra fields in case LJ adds more metadata
    )
