"""API client for downloading LiveJournal posts."""

from datetime import datetime
from typing import Iterator

from yalje.api.base import BaseAPIClient
from yalje.core.config import YaljeConfig
from yalje.core.session import HTTPSession
from yalje.models.post import Post


class PostsClient(BaseAPIClient):
    """Client for downloading posts via LiveJournal export API."""

    def __init__(self, session: HTTPSession, config: YaljeConfig):
        """Initialize posts client.

        Args:
            session: Authenticated HTTP session
            config: Configuration object
        """
        super().__init__(session, config)

    def download_month(self, year: int, month: int) -> list[Post]:
        """Download all posts for a specific month.

        Args:
            year: Year (e.g., 2023)
            month: Month (1-12)

        Returns:
            List of Post objects for that month

        Raises:
            APIError: If download fails
        """
        # TODO: Implement
        # 1. Build request parameters
        # 2. POST to export_do.bml
        # 3. Parse XML response
        # 4. Convert to Post objects
        raise NotImplementedError("PostsClient.download_month not yet implemented")

    def download_all(
        self,
        start_year: int,
        start_month: int,
        end_year: int,
        end_month: int,
    ) -> list[Post]:
        """Download all posts within a date range.

        Args:
            start_year: Starting year
            start_month: Starting month (1-12)
            end_year: Ending year
            end_month: Ending month (1-12)

        Returns:
            List of all Post objects

        Raises:
            APIError: If download fails
        """
        all_posts = []

        for year, month in self._generate_month_range(start_year, start_month, end_year, end_month):
            posts = self.download_month(year, month)
            all_posts.extend(posts)

        return all_posts

    def _generate_month_range(
        self, start_year: int, start_month: int, end_year: int, end_month: int
    ) -> Iterator[tuple[int, int]]:
        """Generate (year, month) tuples for date range.

        Args:
            start_year: Starting year
            start_month: Starting month (1-12)
            end_year: Ending year
            end_month: Ending month (1-12)

        Yields:
            (year, month) tuples
        """
        current = datetime(start_year, start_month, 1)
        end = datetime(end_year, end_month, 1)

        while current <= end:
            yield (current.year, current.month)

            # Move to next month
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1)
            else:
                current = datetime(current.year, current.month + 1, 1)
