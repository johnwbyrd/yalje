"""Data validation utilities."""

from yalje.models.comment import Comment
from yalje.models.export import LJExport
from yalje.models.post import Post
from yalje.models.user import User


def validate_export(export: LJExport) -> list[str]:
    """Validate export data for consistency.

    Args:
        export: LJExport object to validate

    Returns:
        List of validation warnings/errors
    """
    errors = []

    # Validate posts
    errors.extend(_validate_posts(export.posts))

    # Validate comments
    errors.extend(_validate_comments(export.comments, export.posts, export.usermap))

    return errors


def _validate_posts(posts: list[Post]) -> list[str]:
    """Validate posts data.

    Args:
        posts: List of posts

    Returns:
        List of validation errors
    """
    errors = []

    # Check for duplicate itemids
    itemids = [p.itemid for p in posts]
    if len(itemids) != len(set(itemids)):
        errors.append("Duplicate itemids found in posts")

    # Check for duplicate jitemids (if present)
    jitemids = [p.jitemid for p in posts if p.jitemid is not None]
    if len(jitemids) != len(set(jitemids)):
        errors.append("Duplicate jitemids found in posts")

    return errors


def _validate_comments(
    comments: list[Comment], posts: list[Post], usermap: list[User]
) -> list[str]:
    """Validate comments data.

    Args:
        comments: List of comments
        posts: List of posts
        usermap: List of users

    Returns:
        List of validation errors
    """
    errors = []

    # Build lookup sets
    post_jitemids = {p.jitemid for p in posts}
    comment_ids = {c.id for c in comments}
    user_ids = {u.userid for u in usermap}

    for comment in comments:
        # Validate jitemid links to a post
        if comment.jitemid not in post_jitemids:
            errors.append(
                f"Comment {comment.id}: jitemid {comment.jitemid} does not match any post"
            )

        # Validate parentid exists
        if comment.parentid is not None and comment.parentid not in comment_ids:
            errors.append(f"Comment {comment.id}: parentid {comment.parentid} does not exist")

        # Validate posterid in usermap
        if comment.posterid is not None and comment.posterid not in user_ids:
            errors.append(f"Comment {comment.id}: posterid {comment.posterid} not in usermap")

    return errors
