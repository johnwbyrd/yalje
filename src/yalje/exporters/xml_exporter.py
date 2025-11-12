"""XML exporter for LiveJournal data."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, overload

from yalje.core.exceptions import ExportError
from yalje.models.comment import Comment
from yalje.models.export import LJExport
from yalje.models.inbox import InboxMessage
from yalje.models.post import Post
from yalje.models.user import User


class XMLExporter:
    """Exports LiveJournal data to XML format."""

    def export(self, data: LJExport, output_path: Path) -> None:
        """Export data to XML file.

        Args:
            data: LJExport object containing all data
            output_path: Path to write XML file

        Raises:
            ExportError: If export fails
        """
        try:
            # Update metadata counts
            data.update_counts()

            # Generate XML string
            xml_string = self.export_string(data)

            # Write to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(xml_string)

        except Exception as e:
            raise ExportError(f"Failed to export to XML: {e}") from e

    def export_string(self, data: LJExport) -> str:
        """Export data to XML string.

        Args:
            data: LJExport object containing all data

        Returns:
            XML string

        Raises:
            ExportError: If export fails
        """
        try:
            # Update metadata counts
            data.update_counts()

            # Create root element
            root = ET.Element("lj_export")

            # Add metadata
            self._add_metadata(root, data)

            # Add usermap
            self._add_usermap(root, data.usermap)

            # Add posts
            self._add_posts(root, data.posts)

            # Add comments
            self._add_comments(root, data.comments)

            # Add inbox
            self._add_inbox(root, data.inbox)

            # Convert to string with XML declaration
            xml_string = self._prettify(root)
            return xml_string

        except Exception as e:
            raise ExportError(f"Failed to export to XML string: {e}") from e

    @staticmethod
    def load(input_path: Path) -> LJExport:
        """Load data from XML file.

        Args:
            input_path: Path to XML file

        Returns:
            LJExport object

        Raises:
            ExportError: If load fails
        """
        try:
            tree = ET.parse(input_path)
            root = tree.getroot()

            # Parse metadata
            metadata_dict = XMLExporter._parse_metadata(root)

            # Parse usermap
            usermap = XMLExporter._parse_usermap(root)

            # Parse posts
            posts = XMLExporter._parse_posts(root)

            # Parse comments
            comments = XMLExporter._parse_comments(root)

            # Parse inbox
            inbox = XMLExporter._parse_inbox(root)

            # Create LJExport object
            from yalje.models.export import ExportMetadata

            metadata = ExportMetadata(**metadata_dict)
            return LJExport(
                metadata=metadata,
                usermap=usermap,
                posts=posts,
                comments=comments,
                inbox=inbox,
            )

        except Exception as e:
            raise ExportError(f"Failed to load from XML: {e}") from e

    def _add_metadata(self, root: ET.Element, data: LJExport) -> None:
        """Add metadata section to XML."""
        metadata = ET.SubElement(root, "metadata")
        self._add_text_element(metadata, "export_date", data.metadata.export_date)
        self._add_text_element(metadata, "lj_user", data.metadata.lj_user)
        self._add_text_element(metadata, "yalje_version", data.metadata.yalje_version)
        self._add_text_element(metadata, "post_count", str(data.metadata.post_count))
        self._add_text_element(metadata, "comment_count", str(data.metadata.comment_count))
        self._add_text_element(metadata, "inbox_count", str(data.metadata.inbox_count))

    def _add_usermap(self, root: ET.Element, usermap: list[User]) -> None:
        """Add usermap section to XML."""
        usermap_elem = ET.SubElement(root, "usermap")
        for user in usermap:
            user_elem = ET.SubElement(usermap_elem, "user")
            user_elem.set("userid", str(user.userid))
            user_elem.set("username", user.username)

    def _add_posts(self, root: ET.Element, posts: list[Post]) -> None:
        """Add posts section to XML."""
        posts_elem = ET.SubElement(root, "posts")
        for post in posts:
            post_elem = ET.SubElement(posts_elem, "post")
            self._add_text_element(post_elem, "itemid", str(post.itemid))
            self._add_text_element(
                post_elem, "jitemid", str(post.jitemid) if post.jitemid else None
            )
            self._add_text_element(post_elem, "eventtime", post.eventtime)
            self._add_text_element(post_elem, "logtime", post.logtime)
            self._add_text_element(post_elem, "subject", post.subject)
            self._add_cdata_element(post_elem, "event", post.event)
            self._add_text_element(post_elem, "security", post.security)
            self._add_text_element(post_elem, "allowmask", str(post.allowmask))
            self._add_text_element(post_elem, "current_mood", post.current_mood)
            self._add_text_element(post_elem, "current_music", post.current_music)

    def _add_comments(self, root: ET.Element, comments: list[Comment]) -> None:
        """Add comments section to XML."""
        comments_elem = ET.SubElement(root, "comments")
        for comment in comments:
            comment_elem = ET.SubElement(comments_elem, "comment")
            self._add_text_element(comment_elem, "id", str(comment.id))
            self._add_text_element(comment_elem, "jitemid", str(comment.jitemid))
            self._add_text_element(
                comment_elem, "posterid", str(comment.posterid) if comment.posterid else None
            )
            self._add_text_element(comment_elem, "poster_username", comment.poster_username)
            self._add_text_element(
                comment_elem, "parentid", str(comment.parentid) if comment.parentid else None
            )
            self._add_text_element(comment_elem, "date", comment.date)
            self._add_text_element(comment_elem, "subject", comment.subject)
            self._add_cdata_element(comment_elem, "body", comment.body)
            self._add_text_element(comment_elem, "state", comment.state)

    def _add_inbox(self, root: ET.Element, inbox: list[InboxMessage]) -> None:
        """Add inbox section to XML."""
        inbox_elem = ET.SubElement(root, "inbox")
        for message in inbox:
            message_elem = ET.SubElement(inbox_elem, "message")
            self._add_text_element(message_elem, "qid", str(message.qid))
            self._add_text_element(
                message_elem, "msgid", str(message.msgid) if message.msgid else None
            )
            self._add_text_element(message_elem, "type", message.type)

            # Add sender if present
            if message.sender:
                sender_elem = ET.SubElement(message_elem, "sender")
                self._add_text_element(sender_elem, "username", message.sender.username)
                self._add_text_element(sender_elem, "display_name", message.sender.display_name)
                self._add_text_element(sender_elem, "profile_url", message.sender.profile_url)
                self._add_text_element(sender_elem, "userpic_url", message.sender.userpic_url)
                self._add_text_element(
                    sender_elem, "verified", str(message.sender.verified).lower()
                )

            self._add_text_element(message_elem, "title", message.title)
            self._add_cdata_element(message_elem, "body", message.body)
            self._add_text_element(message_elem, "timestamp_relative", message.timestamp_relative)
            self._add_text_element(message_elem, "timestamp_absolute", message.timestamp_absolute)
            self._add_text_element(message_elem, "read", str(message.read).lower())
            self._add_text_element(message_elem, "bookmarked", str(message.bookmarked).lower())

    def _add_text_element(self, parent: ET.Element, tag: str, text: Optional[str]) -> None:
        """Add a text element to parent, handling None values."""
        elem = ET.SubElement(parent, tag)
        if text is not None:
            elem.text = text

    def _add_cdata_element(self, parent: ET.Element, tag: str, text: Optional[str]) -> None:
        """Add an element with CDATA content."""
        elem = ET.SubElement(parent, tag)
        if text is not None:
            # ElementTree doesn't support CDATA directly, so we'll use regular text
            # but escape special characters properly
            elem.text = text

    def _prettify(self, elem: ET.Element) -> str:
        """Return a pretty-printed XML string."""
        # Add indentation
        self._indent(elem)

        # Convert to string with XML declaration
        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_str += ET.tostring(elem, encoding="unicode")
        return xml_str

    def _indent(self, elem: ET.Element, level: int = 0) -> None:
        """Add indentation to XML elements for pretty printing."""
        indent = "\n" + "  " * level
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
            for child in elem:
                self._indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent

    @staticmethod
    def _parse_metadata(root: ET.Element) -> dict:
        """Parse metadata section from XML."""
        metadata_elem = root.find("metadata")
        if metadata_elem is None:
            raise ValueError("Missing metadata section")

        return {
            "export_date": XMLExporter._get_text(metadata_elem, "export_date"),
            "lj_user": XMLExporter._get_text(metadata_elem, "lj_user"),
            "yalje_version": XMLExporter._get_text(metadata_elem, "yalje_version"),
            "post_count": int(XMLExporter._get_text(metadata_elem, "post_count", "0")),
            "comment_count": int(XMLExporter._get_text(metadata_elem, "comment_count", "0")),
            "inbox_count": int(XMLExporter._get_text(metadata_elem, "inbox_count", "0")),
        }

    @staticmethod
    def _parse_usermap(root: ET.Element) -> list[User]:
        """Parse usermap section from XML."""
        usermap_elem = root.find("usermap")
        if usermap_elem is None:
            return []

        usermap = []
        for user_elem in usermap_elem.findall("user"):
            userid = int(user_elem.get("userid", "0"))
            username = user_elem.get("username", "")
            usermap.append(User(userid=userid, username=username))

        return usermap

    @staticmethod
    def _parse_posts(root: ET.Element) -> list[Post]:
        """Parse posts section from XML."""
        posts_elem = root.find("posts")
        if posts_elem is None:
            return []

        posts = []
        for post_elem in posts_elem.findall("post"):
            jitemid_str = XMLExporter._get_text(post_elem, "jitemid")

            post = Post(
                itemid=int(XMLExporter._get_text(post_elem, "itemid", "0")),
                jitemid=int(jitemid_str) if jitemid_str and jitemid_str != "None" else None,
                eventtime=XMLExporter._get_text(post_elem, "eventtime", ""),
                logtime=XMLExporter._get_text(post_elem, "logtime", ""),
                subject=XMLExporter._get_text(post_elem, "subject"),
                event=XMLExporter._get_text(post_elem, "event", ""),
                security=XMLExporter._get_text(post_elem, "security", "public"),
                allowmask=int(XMLExporter._get_text(post_elem, "allowmask", "0")),
                current_mood=XMLExporter._get_text(post_elem, "current_mood"),
                current_music=XMLExporter._get_text(post_elem, "current_music"),
            )
            posts.append(post)

        return posts

    @staticmethod
    def _parse_comments(root: ET.Element) -> list[Comment]:
        """Parse comments section from XML."""
        comments_elem = root.find("comments")
        if comments_elem is None:
            return []

        comments = []
        for comment_elem in comments_elem.findall("comment"):
            posterid_str = XMLExporter._get_text(comment_elem, "posterid")
            parentid_str = XMLExporter._get_text(comment_elem, "parentid")

            comment = Comment(
                id=int(XMLExporter._get_text(comment_elem, "id", "0")),
                jitemid=int(XMLExporter._get_text(comment_elem, "jitemid", "0")),
                posterid=int(posterid_str) if posterid_str and posterid_str != "None" else None,
                poster_username=XMLExporter._get_text(comment_elem, "poster_username"),
                parentid=int(parentid_str) if parentid_str and parentid_str != "None" else None,
                date=XMLExporter._get_text(comment_elem, "date", ""),
                subject=XMLExporter._get_text(comment_elem, "subject"),
                body=XMLExporter._get_text(comment_elem, "body"),
                state=XMLExporter._get_text(comment_elem, "state"),
            )
            comments.append(comment)

        return comments

    @staticmethod
    def _parse_inbox(root: ET.Element) -> list[InboxMessage]:
        """Parse inbox section from XML."""
        inbox_elem = root.find("inbox")
        if inbox_elem is None:
            return []

        inbox = []
        for message_elem in inbox_elem.findall("message"):
            msgid_str = XMLExporter._get_text(message_elem, "msgid")

            # Parse sender if present
            sender = None
            sender_elem = message_elem.find("sender")
            if sender_elem is not None:
                from yalje.models.user import InboxSender

                sender = InboxSender(
                    username=XMLExporter._get_text(sender_elem, "username", ""),
                    display_name=XMLExporter._get_text(sender_elem, "display_name", ""),
                    profile_url=XMLExporter._get_text(sender_elem, "profile_url", ""),
                    userpic_url=XMLExporter._get_text(sender_elem, "userpic_url"),
                    verified=XMLExporter._get_text(sender_elem, "verified", "false") == "true",
                )

            message = InboxMessage(
                qid=int(XMLExporter._get_text(message_elem, "qid", "0")),
                msgid=int(msgid_str) if msgid_str and msgid_str != "None" else None,
                type=XMLExporter._get_text(message_elem, "type", ""),
                sender=sender,
                title=XMLExporter._get_text(message_elem, "title", ""),
                body=XMLExporter._get_text(message_elem, "body", ""),
                timestamp_relative=XMLExporter._get_text(message_elem, "timestamp_relative", ""),
                timestamp_absolute=XMLExporter._get_text(message_elem, "timestamp_absolute"),
                read=XMLExporter._get_text(message_elem, "read", "false") == "true",
                bookmarked=XMLExporter._get_text(message_elem, "bookmarked", "false") == "true",
            )
            inbox.append(message)

        return inbox

    @overload
    @staticmethod
    def _get_text(element: ET.Element, tag: str, default: str) -> str: ...

    @overload
    @staticmethod
    def _get_text(element: ET.Element, tag: str, default: None = None) -> Optional[str]: ...

    @staticmethod
    def _get_text(element: ET.Element, tag: str, default: Optional[str] = None) -> Optional[str]:
        """Get text content from child element."""
        child = element.find(tag)
        if child is not None and child.text:
            return child.text
        return default
