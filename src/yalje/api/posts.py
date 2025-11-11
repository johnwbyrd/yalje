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
        from yalje.parsers.xml_parser import XMLParser

        # Build request parameters
        data = {
            "what": "journal",
            "year": str(year),
            "month": f"{month:02d}",  # Zero-padded month
            "format": "xml",
            "header": "on",
            "encid": "2",  # UTF-8 encoding
            "field_itemid": "on",
            "field_eventtime": "on",
            "field_logtime": "on",
            "field_subject": "on",
            "field_event": "on",
            "field_security": "on",
            "field_allowmask": "on",
            "field_currents": "on",
        }

        # Build URL
        url = self._build_url("/export_do.bml")

        # Make POST request
        response = self.session.post(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Parse XML response
        posts = XMLParser.parse_posts(response.text)

        return posts

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
