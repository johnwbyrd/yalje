"""Top-level export model containing all LiveJournal data."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from yalje.models.comment import Comment
from yalje.models.inbox import InboxMessage
from yalje.models.post import Post
from yalje.models.user import User


class ExportMetadata(BaseModel):
    """Metadata about the export operation."""

    export_date: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="When export was performed (ISO 8601)",
    )
    lj_user: str = Field(..., description="LiveJournal username")
    yalje_version: str = Field(..., description="Version of yalje used")
    post_count: int = Field(0, description="Total number of posts")
    comment_count: int = Field(0, description="Total number of comments")
    inbox_count: int = Field(0, description="Total number of inbox messages")


class LJExport(BaseModel):
    """
    Complete LiveJournal export data.

    This is the top-level model that gets serialized to YAML.
    Contains all posts, comments, and inbox messages in a single structure.
    """

    metadata: ExportMetadata = Field(..., description="Export metadata")
    usermap: list[User] = Field(
        default_factory=list, description="User ID to username mappings"
    )
    posts: list[Post] = Field(default_factory=list, description="All blog posts")
    comments: list[Comment] = Field(default_factory=list, description="All comments")
    inbox: list[InboxMessage] = Field(
        default_factory=list, description="All inbox messages"
    )

    def to_yaml(self) -> str:
        """
        Serialize the export to YAML format.

        Returns:
            YAML string representation of the entire export
        """
        import yaml

        # Convert to dict using pydantic's model_dump
        data = self.model_dump(mode="python", exclude_none=False)

        # Serialize to YAML with nice formatting
        return yaml.dump(
            data,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=100,
        )

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "LJExport":
        """
        Load an export from YAML format.

        Args:
            yaml_str: YAML string

        Returns:
            LJExport instance
        """
        import yaml

        data = yaml.safe_load(yaml_str)
        return cls(**data)

    @classmethod
    def from_file(cls, path: str) -> "LJExport":
        """
        Load an export from a YAML file.

        Args:
            path: Path to YAML file

        Returns:
            LJExport instance
        """
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_yaml(f.read())

    def to_file(self, path: str) -> None:
        """
        Write the export to a YAML file.

        Args:
            path: Path to write YAML file
        """
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_yaml())

    def update_counts(self) -> None:
        """Update metadata counts based on current data."""
        self.metadata.post_count = len(self.posts)
        self.metadata.comment_count = len(self.comments)
        self.metadata.inbox_count = len(self.inbox)

    class Config:
        """Pydantic config."""

        extra = "ignore"
