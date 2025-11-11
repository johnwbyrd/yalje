"""API client for downloading LiveJournal comments."""

from yalje.api.base import BaseAPIClient
from yalje.core.config import YaljeConfig
from yalje.core.session import HTTPSession
from yalje.models.comment import Comment
from yalje.models.user import User
from yalje.utils.logging import get_logger

logger = get_logger("api.comments")


class CommentsClient(BaseAPIClient):
    """Client for downloading comments via LiveJournal export API."""

    def __init__(self, session: HTTPSession, config: YaljeConfig):
        """Initialize comments client.

        Args:
            session: Authenticated HTTP session
            config: Configuration object
        """
        super().__init__(session, config)

    def download_metadata(self) -> tuple[int, list[User]]:
        """Download comment metadata (maxid and usermap).

        Returns:
            Tuple of (maxid, usermap)
            - maxid: Highest comment ID
            - usermap: List of User objects

        Raises:
            APIError: If download fails
        """
        from yalje.parsers.xml_parser import XMLParser

        logger.info("Downloading comment metadata")

        # Build URL
        url = self._build_url("/export_comments.bml")

        # Add query parameters
        params = {"get": "comment_meta", "startid": "0"}

        # Make GET request
        response = self.session.get(url, params=params)

        # Parse XML response
        maxid, usermap = XMLParser.parse_comment_metadata(response.text)

        logger.info(f"  → Downloaded metadata: maxid={maxid}, {len(usermap)} users in usermap")
        return (maxid, usermap)

    def download_all(self) -> tuple[list[Comment], list[User]]:
        """Download all comments with usermap.

        Returns:
            Tuple of (comments, usermap)
            - comments: List of all Comment objects
            - usermap: List of User objects

        Raises:
            APIError: If download fails
        """
        # Get metadata first
        maxid, usermap = self.download_metadata()

        # Download comment bodies in batches
        all_comments = []
        startid = 0

        while startid < maxid:
            batch = self.download_batch(startid)
            if not batch:
                break

            all_comments.extend(batch)

            # Update startid to highest ID in batch
            startid = max(c.id for c in batch)

        # Resolve poster usernames
        self._resolve_usernames(all_comments, usermap)

        return all_comments, usermap

    def download_batch(self, startid: int) -> list[Comment]:
        """Download a batch of comments starting after startid.

        Args:
            startid: Start ID (downloads comments with ID > startid)

        Returns:
            List of Comment objects in this batch

        Raises:
            APIError: If download fails
        """
        from yalje.parsers.xml_parser import XMLParser

        logger.info(f"Downloading comments batch starting from ID {startid}")

        # Build URL
        url = self._build_url("/export_comments.bml")

        # Add query parameters
        params = {"get": "comment_body", "startid": str(startid)}

        # Make GET request
        response = self.session.get(url, params=params)

        # Parse XML response
        comments = XMLParser.parse_comments(response.text)

        logger.info(f"  → Downloaded {len(comments)} comments in batch")
        return comments

    def _resolve_usernames(self, comments: list[Comment], usermap: list[User]) -> None:
        """Resolve poster_username for comments using usermap.

        Args:
            comments: List of comments to update
            usermap: User ID to username mappings
        """
        # Build lookup dict
        user_lookup = {user.userid: user.username for user in usermap}

        # Resolve usernames
        for comment in comments:
            if comment.posterid is not None:
                comment.poster_username = user_lookup.get(
                    comment.posterid, f"[unknown-{comment.posterid}]"
                )
