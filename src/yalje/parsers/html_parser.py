"""HTML parser for LiveJournal inbox pages."""

import re
from typing import Optional

from bs4 import BeautifulSoup, Tag

from yalje.core.exceptions import ParsingError
from yalje.models.inbox import InboxMessage
from yalje.models.user import InboxSender
from yalje.utils.logging import get_logger

logger = get_logger("parsers.html")


class HTMLParser:
    """Parser for LiveJournal HTML pages (inbox)."""

    @staticmethod
    def parse_inbox_page(html_string: str) -> tuple[list[InboxMessage], bool]:
        """Parse inbox messages from HTML page.

        Args:
            html_string: HTML string from /inbox/

        Returns:
            Tuple of (messages, has_next_page)

        Raises:
            ParsingError: If HTML parsing fails
        """
        logger.debug("Parsing inbox page from HTML")

        try:
            soup = BeautifulSoup(html_string, "html.parser")
        except Exception as e:
            logger.error(f"Failed to parse HTML: {e}")
            raise ParsingError(f"Failed to parse HTML: {e}") from e

        messages = []

        # Find all message rows
        rows = soup.find_all("tr", class_="InboxItem_Row")
        logger.debug(f"Found {len(rows)} message rows")

        for row in rows:
            try:
                message = HTMLParser._extract_message_from_row(row)
                if message:
                    messages.append(message)
            except Exception as e:
                logger.warning(f"Failed to parse message row: {e}")
                continue

        # Extract pagination to determine if there's a next page
        try:
            current_page, total_pages = HTMLParser._extract_pagination(soup)
            has_next_page = current_page < total_pages
            logger.debug(
                f"Pagination: page {current_page} of {total_pages}, has_next={has_next_page}"
            )
        except ParsingError:
            # If pagination info is missing, assume single page
            logger.debug("No pagination info found, assuming single page")
            has_next_page = False

        logger.debug(f"Parsed {len(messages)} messages from inbox page")
        return (messages, has_next_page)

    @staticmethod
    def _extract_message_from_row(row: Tag) -> Optional[InboxMessage]:
        """Extract inbox message from a table row.

        Args:
            row: HTML table row element

        Returns:
            InboxMessage object or None if parsing fails
        """
        # Extract qid from lj_qid attribute
        qid_str = row.get("lj_qid")
        if not qid_str or not isinstance(qid_str, str):
            logger.warning("Message row missing lj_qid attribute")
            return None

        try:
            qid = int(qid_str)
        except ValueError:
            logger.warning(f"Invalid qid value: {qid_str}")
            return None

        # Extract msgid from reply link
        msgid = HTMLParser._extract_msgid(row)

        # Extract read/unread status
        title_span = row.find("span", class_="InboxItem_Title")
        if not title_span:
            logger.warning(f"Message {qid} missing InboxItem_Title span")
            return None

        classes = title_span.get("class")
        is_read = "InboxItem_Read" in classes if isinstance(classes, list) else False

        # Extract bookmarked status (flag_on.gif = bookmarked, flag_off.gif = not bookmarked)
        bookmark_img = row.find("img", class_="InboxItem_Bookmark")
        bookmarked = False
        if bookmark_img:
            bookmark_src = bookmark_img.get("src", "")
            bookmarked = "flag_on.gif" in bookmark_src if isinstance(bookmark_src, str) else False

        # Extract title and sender from InboxItem_Title span
        # The title span contains mixed content, need to extract carefully
        title_text = ""
        sender = HTMLParser._extract_sender(title_span)

        # Extract title - it's the text before "from" or the entire text if no sender
        title_html = str(title_span)
        # Remove the ljuser span to get just the title
        title_soup = BeautifulSoup(title_html, "html.parser")
        ljuser_span = title_soup.find("span", class_="ljuser")
        if ljuser_span:
            ljuser_span.decompose()

        # Get text and clean it
        title_text = title_soup.get_text().strip()
        # Remove "from" and everything after it (including the word "from")
        title_text = re.sub(r"\s*from\s*$", "", title_text).strip()

        if not title_text:
            title_text = "No subject"

        # Extract body from InboxItem_Content div
        content_div = row.find("div", class_="InboxItem_Content")
        body = ""
        if content_div:
            # Clone the content to avoid modifying original
            content_clone = BeautifulSoup(str(content_div), "html.parser")
            # Remove the actions div
            actions_div = content_clone.find("div", class_="actions")
            if actions_div:
                actions_div.decompose()
            # Get the HTML content
            body = content_clone.get_text().strip()
            if not body:
                body = "No content"

        # Extract timestamp from time cell
        time_cell = row.find("td", class_="time")
        timestamp_relative = ""
        if time_cell:
            timestamp_relative = time_cell.get_text().strip()
        else:
            timestamp_relative = "Unknown"

        # Determine message type
        if sender:
            if sender.username == "livejournal" and sender.verified:
                message_type = "official_message"
            else:
                message_type = "user_message"
        else:
            message_type = "system_notification"

        # Create InboxMessage object
        message = InboxMessage(
            qid=qid,
            msgid=msgid,
            type=message_type,
            sender=sender,
            title=title_text,
            body=body,
            timestamp_relative=timestamp_relative,
            timestamp_absolute=None,  # Not available in HTML
            read=is_read,
            bookmarked=bookmarked,
        )

        return message

    @staticmethod
    def _extract_sender(title_span: Tag) -> Optional[InboxSender]:
        """Extract sender information from message title span.

        Args:
            title_span: InboxItem_Title span element

        Returns:
            InboxSender object or None if no sender (system message)
        """
        # Find ljuser span with data-ljuser attribute
        ljuser_span = title_span.find("span", class_="ljuser")
        if not ljuser_span:
            return None

        # Extract username
        username_raw = ljuser_span.get("data-ljuser")
        if not username_raw or not isinstance(username_raw, str):
            return None
        username = username_raw

        # Extract display name (the <b> tag content, or username if not found)
        display_name_tag = ljuser_span.find("b")
        display_name = display_name_tag.get_text().strip() if display_name_tag else username

        # Extract profile URL
        profile_link = ljuser_span.find("a", class_="i-ljuser-profile")
        if profile_link:
            profile_url_raw = profile_link.get(
                "href", f"https://{username}.livejournal.com/profile/"
            )
            profile_url = (
                profile_url_raw
                if isinstance(profile_url_raw, str)
                else f"https://{username}.livejournal.com/profile/"
            )
        else:
            profile_url = f"https://{username}.livejournal.com/profile/"

        # Extract userpic URL (from the userhead img)
        userpic_img = ljuser_span.find("img", class_="i-ljuser-userhead")
        userpic_url: Optional[str] = None
        if userpic_img:
            userpic_src = userpic_img.get("src")
            if isinstance(userpic_src, str):
                userpic_url = userpic_src

        # Check for verified badge
        verified_badge = ljuser_span.find("a", class_="i-ljuser-badge--verified")
        verified = verified_badge is not None

        return InboxSender(
            username=username,
            display_name=display_name,
            profile_url=profile_url,
            userpic_url=userpic_url,
            verified=verified,
        )

    @staticmethod
    def _extract_pagination(soup: BeautifulSoup) -> tuple[int, int]:
        """Extract current page and total pages from HTML.

        Args:
            soup: BeautifulSoup document

        Returns:
            Tuple of (current_page, total_pages)

        Raises:
            ParsingError: If pagination info not found
        """
        # Find element with "Page X of Y" text
        page_number_span = soup.find("span", class_="page-number")
        if not page_number_span:
            raise ParsingError("Pagination info not found")

        page_text = page_number_span.get_text().strip()

        # Extract page numbers using regex
        match = re.search(r"Page\s+(\d+)\s+of\s+(\d+)", page_text)
        if not match:
            raise ParsingError(f"Could not parse pagination text: {page_text}")

        try:
            current_page = int(match.group(1))
            total_pages = int(match.group(2))
            return (current_page, total_pages)
        except ValueError as e:
            raise ParsingError(f"Invalid page numbers in pagination: {page_text}") from e

    @staticmethod
    def _extract_msgid(row: Tag) -> Optional[int]:
        """Extract message ID from reply link.

        Args:
            row: HTML table row element

        Returns:
            Message ID or None if not found
        """
        # Find link with href containing "msgid="
        actions_div = row.find("div", class_="actions")
        if not actions_div:
            return None

        # Look for reply link
        reply_link = actions_div.find("a", href=re.compile(r"msgid="))
        if not reply_link:
            return None

        href_raw = reply_link.get("href", "")
        if not isinstance(href_raw, str):
            return None
        href = href_raw

        # Extract msgid parameter value
        match = re.search(r"msgid=(\d+)", href)
        if not match:
            return None

        try:
            return int(match.group(1))
        except ValueError:
            return None
