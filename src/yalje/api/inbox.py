"""API client (HTML scraper) for downloading LiveJournal inbox messages."""

from typing import Optional

from yalje.api.base import BaseAPIClient
from yalje.core.config import YaljeConfig
from yalje.core.session import HTTPSession
from yalje.models.inbox import InboxMessage
from yalje.utils.logging import get_logger

logger = get_logger("api.inbox")


class InboxClient(BaseAPIClient):
    """Client for scraping inbox messages via HTML."""

    def __init__(self, session: HTTPSession, config: YaljeConfig):
        """Initialize inbox client.

        Args:
            session: Authenticated HTTP session
            config: Configuration object
        """
        super().__init__(session, config)

    def download_folder(self, view: str = "all") -> list[InboxMessage]:
        """Download all messages from a specific inbox folder.

        Args:
            view: Folder view (all, usermsg_recvd, ljmsg_recvd, friendplus, etc.)

        Returns:
            List of InboxMessage objects

        Raises:
            APIError: If download fails
        """
        logger.info(f"Downloading inbox folder: {view}")
        all_messages = []
        page = 1

        while True:
            messages, has_next = self.download_page(view, page)
            all_messages.extend(messages)

            if not has_next:
                break

            page += 1

        logger.info(f"  → Downloaded {len(all_messages)} messages from folder '{view}'")
        return all_messages

    def download_page(self, view: str, page: int) -> tuple[list[InboxMessage], bool]:
        """Download a single page of inbox messages.

        Args:
            view: Folder view
            page: Page number (1-indexed)

        Returns:
            Tuple of (messages, has_next_page)
            - messages: List of InboxMessage objects on this page
            - has_next_page: Whether there are more pages

        Raises:
            APIError: If download fails
        """
        from yalje.parsers.html_parser import HTMLParser

        logger.info(f"Downloading inbox page {page} (view={view})")

        # Build URL with query parameters
        url = self._build_url("/inbox/")
        params = {"view": view, "page": str(page)}

        # Make GET request
        response = self.session.get(url, params=params)

        # Parse HTML response using HTMLParser
        messages, has_next_page = HTMLParser.parse_inbox_page(response.text)

        logger.info(f"  → Downloaded {len(messages)} messages from page {page}")
        return (messages, has_next_page)

    def download_all(self, folders: Optional[list[str]] = None) -> list[InboxMessage]:
        """Download messages from multiple inbox folders.

        Args:
            folders: List of folder views (defaults to ['all'])

        Returns:
            List of all InboxMessage objects (may contain duplicates across folders)

        Raises:
            APIError: If download fails
        """
        if folders is None:
            folders = ["all"]

        all_messages = []
        for folder in folders:
            messages = self.download_folder(folder)
            all_messages.extend(messages)

        return all_messages
