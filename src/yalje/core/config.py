"""Configuration management for yalje."""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class YaljeConfig(BaseModel):
    """Configuration for yalje operations."""

    # Authentication
    username: Optional[str] = None
    password: Optional[str] = None

    # Paths
    output_path: Path = Field(default=Path("lj-backup.yaml"))
    config_dir: Path = Field(default=Path.home() / ".yalje")

    # API settings
    base_url: str = "https://www.livejournal.com"
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    )
    request_timeout: int = 30  # seconds
    retry_attempts: int = 3
    retry_backoff: float = 1.0  # seconds

    # Rate limiting
    request_delay: float = 1.0  # seconds between requests

    # Export options
    export_posts: bool = True
    export_comments: bool = True
    export_inbox: bool = True
    inbox_folders: list[str] = Field(
        default_factory=lambda: ["all"]  # Default to 'all' folder
    )

    # Date range for posts (None = all time)
    posts_start_year: Optional[int] = None
    posts_start_month: Optional[int] = None
    posts_end_year: Optional[int] = None
    posts_end_month: Optional[int] = None

    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True

    def save_to_file(self, path: Path) -> None:
        """Save configuration to a YAML file."""
        import yaml

        with open(path, "w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)

    @classmethod
    def load_from_file(cls, path: Path) -> "YaljeConfig":
        """Load configuration from a YAML file."""
        import yaml

        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def get_default_config_path(cls) -> Path:
        """Get the default configuration file path."""
        return Path.home() / ".yalje" / "config.yaml"
