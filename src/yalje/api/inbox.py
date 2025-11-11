"""API client (HTML scraper) for downloading LiveJournal inbox messages."""

from yalje.api.base import BaseAPIClient
from yalje.core.config import YaljeConfig
from yalje.core.session import HTTPSession
from yalje.models.inbox import InboxMessage


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
        all_messages = []
        page = 1

        while True:
            messages, has_next = self.download_page(view, page)
            all_messages.extend(messages)

            if not has_next:
                break

            page += 1

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
        # TODO: Implement
        # 1. GET /inbox/?view={view}&page={page}
        # 2. Parse HTML response
        # 3. Extract messages from table rows
        # 4. Check pagination for more pages
        # 5. Convert to InboxMessage objects
        raise NotImplementedError("InboxClient.download_page not yet implemented")

    def download_all(self, folders: list[str] = None) -> list[InboxMessage]:
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
