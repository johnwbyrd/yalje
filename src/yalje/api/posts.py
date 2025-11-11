"""API client for downloading LiveJournal posts."""

from datetime import datetime
from typing import Iterator, Optional

from yalje.api.base import BaseAPIClient
from yalje.core.config import YaljeConfig
from yalje.core.session import HTTPSession
from yalje.models.post import Post
from yalje.utils.logging import get_logger

logger = get_logger("api.posts")


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

        logger.info(f"Downloading posts for {year}-{month:02d}")

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

        logger.info(f"  → Downloaded {len(posts)} posts for {year}-{month:02d}")
        return posts

    def discover_date_range(self) -> tuple[tuple[int, int], tuple[int, int], int]:
        """Discover date range and post count from user's profile page.

        Fetches the profile page and extracts:
        - Journal creation date (start bound)
        - Last update date (end bound)
        - Total post count (for validation)

        Returns:
            Tuple of ((start_year, start_month), (end_year, end_month), post_count)

        Raises:
            APIError: If profile cannot be fetched
            ParsingError: If profile data cannot be parsed
        """
        from yalje.api.profile import ProfileParser

        logger.info("Auto-discovering date range from profile page")

        # Fetch profile page
        profile_url = f"https://{self.config.username}.livejournal.com/profile/"
        response = self.session.get(profile_url)

        # Parse profile data
        profile_data = ProfileParser.parse_profile_data(response.text)

        start_date = (profile_data.created_year, profile_data.created_month)
        end_date = (profile_data.updated_year, profile_data.updated_month)
        post_count = profile_data.post_count

        logger.info(
            f"  → Discovered: {post_count} posts from "
            f"{start_date[0]}-{start_date[1]:02d} to {end_date[0]}-{end_date[1]:02d}"
        )

        return (start_date, end_date, post_count)

    def download_all(
        self,
        start_year: Optional[int] = None,
        start_month: Optional[int] = None,
        end_year: Optional[int] = None,
        end_month: Optional[int] = None,
    ) -> list[Post]:
        """Download all posts within a date range.

        If no date parameters are provided, automatically discovers the range
        from the user's profile page.

        Args:
            start_year: Starting year (optional - auto-discovered if not provided)
            start_month: Starting month 1-12 (optional - auto-discovered if not provided)
            end_year: Ending year (optional - auto-discovered if not provided)
            end_month: Ending month 1-12 (optional - auto-discovered if not provided)

        Returns:
            List of all Post objects

        Raises:
            APIError: If download fails
            ParsingError: If profile parsing fails during auto-discovery
        """
        # Auto-discover date range if not provided
        expected_count = None
        if start_year is None or end_year is None:
            (start_year, start_month), (end_year, end_month), expected_count = (
                self.discover_date_range()
            )
            logger.info(f"Auto-discovered range: expecting {expected_count} posts")

        # Type narrowing: after auto-discovery, these values are guaranteed to be int
        assert start_year is not None and start_month is not None
        assert end_year is not None and end_month is not None

        all_posts = []

        for year, month in self._generate_month_range(start_year, start_month, end_year, end_month):
            posts = self.download_month(year, month)
            all_posts.extend(posts)

        # Log validation if we have expected count
        if expected_count is not None:
            if len(all_posts) == expected_count:
                logger.info(f"✓ Downloaded all {len(all_posts)} posts (matches profile count)")
            else:
                logger.warning(
                    f"Downloaded {len(all_posts)} posts but profile shows {expected_count} "
                    f"(difference may be due to deleted/private posts)"
                )

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
