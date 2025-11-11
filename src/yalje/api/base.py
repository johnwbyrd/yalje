"""Base API client with common functionality."""

from yalje.core.config import YaljeConfig
from yalje.core.session import HTTPSession


class BaseAPIClient:
    """Base class for all API clients."""

    def __init__(self, session: HTTPSession, config: YaljeConfig):
        """Initialize API client.

        Args:
            session: Authenticated HTTP session
            config: Configuration object
        """
        self.session = session
        self.config = config
        self.base_url = config.base_url

    def _build_url(self, path: str) -> str:
        """Build full URL from path.

        Args:
            path: URL path (e.g., "/export_do.bml")

        Returns:
            Full URL
        """
        return f"{self.base_url}{path}"
