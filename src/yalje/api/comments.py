"""API client for downloading LiveJournal comments."""

from yalje.api.base import BaseAPIClient
from yalje.core.config import YaljeConfig
from yalje.core.session import HTTPSession
from yalje.models.comment import Comment
from yalje.models.user import User


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
        # TODO: Implement
        # 1. GET export_comments.bml?get=comment_meta&startid=0
        # 2. Parse XML response
        # 3. Extract maxid and usermap
        raise NotImplementedError("CommentsClient.download_metadata not yet implemented")

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
        # TODO: Implement
        # 1. GET export_comments.bml?get=comment_body&startid={startid}
        # 2. Parse XML response
        # 3. Convert to Comment objects
        raise NotImplementedError("CommentsClient.download_batch not yet implemented")

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
