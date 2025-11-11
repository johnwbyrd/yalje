"""XML parser for LiveJournal posts and comments."""

from typing import Optional
from xml.etree import ElementTree as ET

from yalje.models.comment import Comment
from yalje.models.post import Post
from yalje.models.user import User
from yalje.utils.logging import get_logger

logger = get_logger("parsers.xml")


class XMLParser:
    """Parser for LiveJournal XML responses."""

    @staticmethod
    def parse_posts(xml_string: str) -> list[Post]:
        """Parse posts from XML response.

        Args:
            xml_string: XML string from export_do.bml

        Returns:
            List of Post objects

        Raises:
            ParsingError: If XML parsing fails
        """
        from yalje.core.exceptions import ParsingError

        logger.debug("Parsing posts from XML")

        try:
            # Parse XML string
            root = ET.fromstring(xml_string)
        except ET.ParseError as e:
            logger.error(f"XML parsing failed: {e}")
            raise ParsingError(f"Failed to parse XML: {e}") from e

        posts = []

        # Find all <entry> elements
        for entry in root.findall("entry"):
            try:
                # Extract required fields
                itemid = XMLParser._get_int(entry, "itemid")
                if itemid is None:
                    raise ParsingError("Missing required field: itemid")

                eventtime = XMLParser._get_text(entry, "eventtime")
                if eventtime is None:
                    raise ParsingError(f"Missing required field: eventtime for itemid {itemid}")

                logtime = XMLParser._get_text(entry, "logtime")
                if logtime is None:
                    raise ParsingError(f"Missing required field: logtime for itemid {itemid}")

                event = XMLParser._get_text(entry, "event")
                if event is None:
                    raise ParsingError(f"Missing required field: event for itemid {itemid}")

                security = XMLParser._get_text(entry, "security")
                if security is None:
                    raise ParsingError(f"Missing required field: security for itemid {itemid}")

                # Extract optional fields
                subject = XMLParser._get_text(entry, "subject")
                # Convert empty string to None for subject
                if subject == "":
                    subject = None

                allowmask = XMLParser._get_int(entry, "allowmask")
                if allowmask is None:
                    allowmask = 0

                current_mood = XMLParser._get_text(entry, "current_mood")
                current_music = XMLParser._get_text(entry, "current_music")

                # Extract jitemid (optional field)
                jitemid = XMLParser._get_int(entry, "jitemid")

                # Create Post object
                post = Post(
                    itemid=itemid,
                    jitemid=jitemid,
                    eventtime=eventtime,
                    logtime=logtime,
                    subject=subject,
                    event=event,
                    security=security,
                    allowmask=allowmask,
                    current_mood=current_mood,
                    current_music=current_music,
                )
                posts.append(post)

            except Exception as e:
                if isinstance(e, ParsingError):
                    raise
                logger.error(f"Failed to parse entry: {e}")
                raise ParsingError(f"Failed to parse entry: {e}") from e

        logger.debug(f"  → Parsed {len(posts)} posts from XML")
        return posts

    @staticmethod
    def parse_comment_metadata(xml_string: str) -> tuple[int, list[User]]:
        """Parse comment metadata from XML response.

        Args:
            xml_string: XML string from export_comments.bml?get=comment_meta

        Returns:
            Tuple of (maxid, usermap)

        Raises:
            ParsingError: If XML parsing fails
        """
        from yalje.core.exceptions import ParsingError

        logger.debug("Parsing comment metadata from XML")

        try:
            # Parse XML string
            root = ET.fromstring(xml_string)
        except ET.ParseError as e:
            logger.error(f"XML parsing failed: {e}")
            raise ParsingError(f"Failed to parse XML: {e}") from e

        # Extract maxid (required)
        maxid_elem = root.find("maxid")
        if maxid_elem is None or maxid_elem.text is None:
            logger.error("Missing required field: maxid")
            raise ParsingError("Missing required field: maxid")

        try:
            maxid = int(maxid_elem.text)
        except ValueError as e:
            logger.error(f"Invalid maxid value: {maxid_elem.text}")
            raise ParsingError(f"Invalid maxid value: {maxid_elem.text}") from e

        # Extract all usermap elements
        usermap = []
        for usermap_elem in root.findall("usermap"):
            try:
                # Get attributes
                userid_str = usermap_elem.get("id")
                username = usermap_elem.get("user")

                if userid_str is None:
                    logger.warning("Skipping usermap element without 'id' attribute")
                    continue

                if username is None:
                    logger.warning(
                        f"Skipping usermap element without 'user' attribute (id={userid_str})"
                    )
                    continue

                # Convert userid to int
                userid = int(userid_str)

                # Create User object
                user = User(userid=userid, username=username)
                usermap.append(user)

            except ValueError:
                logger.warning(f"Skipping usermap with invalid userid: {userid_str}")
                continue
            except Exception as e:
                logger.warning(f"Failed to parse usermap element: {e}")
                continue

        logger.debug(f"  → Parsed maxid={maxid}, {len(usermap)} users from XML")
        return (maxid, usermap)

    @staticmethod
    def parse_comments(xml_string: str) -> list[Comment]:
        """Parse comments from XML response.

        Args:
            xml_string: XML string from export_comments.bml?get=comment_body

        Returns:
            List of Comment objects

        Raises:
            ParsingError: If XML parsing fails
        """
        from yalje.core.exceptions import ParsingError

        logger.debug("Parsing comments from XML")

        try:
            # Parse XML string
            root = ET.fromstring(xml_string)
        except ET.ParseError as e:
            logger.error(f"XML parsing failed: {e}")
            raise ParsingError(f"Failed to parse XML: {e}") from e

        comments = []

        # Find all <comment> elements
        for comment_elem in root.findall("comment"):
            try:
                # Extract required attributes
                comment_id_str = comment_elem.get("id")
                if comment_id_str is None:
                    raise ParsingError("Missing required attribute: id")

                jitemid_str = comment_elem.get("jitemid")
                if jitemid_str is None:
                    raise ParsingError("Missing required attribute: jitemid")

                # Convert required attributes to int
                comment_id = int(comment_id_str)
                jitemid = int(jitemid_str)

                # Extract optional attributes
                posterid_str = comment_elem.get("posterid")
                posterid = int(posterid_str) if posterid_str is not None else None

                parentid_str = comment_elem.get("parentid")
                parentid = int(parentid_str) if parentid_str is not None else None

                state_str = comment_elem.get("state")
                # Convert state "D" to "deleted", None to None
                state = "deleted" if state_str == "D" else None

                # Extract required child element: date
                date = XMLParser._get_text(comment_elem, "date")
                if date is None:
                    raise ParsingError(f"Missing required field: date for comment id {comment_id}")

                # Extract optional child elements
                subject = XMLParser._get_text(comment_elem, "subject")
                # Convert empty string to None for subject
                if subject == "":
                    subject = None

                body = XMLParser._get_text(comment_elem, "body")
                # Convert empty string to None for body
                if body == "":
                    body = None

                # Create Comment object (poster_username is None, will be resolved later)
                comment = Comment(
                    id=comment_id,
                    jitemid=jitemid,
                    posterid=posterid,
                    poster_username=None,
                    parentid=parentid,
                    date=date,
                    subject=subject,
                    body=body,
                    state=state,
                )
                comments.append(comment)

            except Exception as e:
                if isinstance(e, ParsingError):
                    raise
                logger.error(f"Failed to parse comment element: {e}")
                raise ParsingError(f"Failed to parse comment element: {e}") from e

        logger.debug(f"  → Parsed {len(comments)} comments from XML")
        return comments

    @staticmethod
    def _get_text(element: ET.Element, tag: str) -> Optional[str]:
        """Get text content from child element.

        Args:
            element: Parent element
            tag: Child tag name

        Returns:
            Text content or None if not found
        """
        child = element.find(tag)
        if child is not None:
            return child.text
        return None

    @staticmethod
    def _get_int(element: ET.Element, tag: str) -> Optional[int]:
        """Get integer content from child element.

        Args:
            element: Parent element
            tag: Child tag name

        Returns:
            Integer value or None if not found
        """
        text = XMLParser._get_text(element, tag)
        if text is not None:
            return int(text)
        return None
