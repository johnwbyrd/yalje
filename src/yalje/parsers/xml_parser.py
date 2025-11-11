"""XML parser for LiveJournal posts and comments."""

from typing import Optional
from xml.etree import ElementTree as ET

from yalje.models.comment import Comment
from yalje.models.post import Post
from yalje.models.user import User


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

        try:
            # Parse XML string
            root = ET.fromstring(xml_string)
        except ET.ParseError as e:
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

                # Create Post object (Pydantic will calculate jitemid automatically)
                post = Post(
                    itemid=itemid,
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
                raise ParsingError(f"Failed to parse entry: {e}") from e

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
        # TODO: Implement
        # 1. Parse XML with lxml
        # 2. Extract <maxid> value
        # 3. Extract all <usermap> elements
        # 4. Convert to User objects
        raise NotImplementedError("XMLParser.parse_comment_metadata not yet implemented")

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
        # TODO: Implement
        # 1. Parse XML with lxml
        # 2. Find all <comment> elements
        # 3. Extract attributes (id, jitemid, posterid, parentid, state)
        # 4. Extract child elements (date, subject, body)
        # 5. Handle CDATA sections in <body>
        # 6. Convert to Comment objects
        raise NotImplementedError("XMLParser.parse_comments not yet implemented")

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
