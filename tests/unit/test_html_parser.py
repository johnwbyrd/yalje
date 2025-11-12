"""Tests for HTML parser (inbox)."""

from pathlib import Path

import pytest

from yalje.core.exceptions import ParsingError
from yalje.parsers.html_parser import HTMLParser


@pytest.fixture
def fixtures_dir() -> Path:
    """Get the fixtures directory path."""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def sample_inbox_real_html(fixtures_dir: Path) -> str:
    """Load real inbox HTML."""
    with open(fixtures_dir / "sample_inbox_real.html", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def sample_inbox_empty_html(fixtures_dir: Path) -> str:
    """Load empty inbox HTML."""
    with open(fixtures_dir / "sample_inbox_empty.html", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def sample_inbox_multipage_html(fixtures_dir: Path) -> str:
    """Load multipage inbox HTML."""
    with open(fixtures_dir / "sample_inbox_multipage.html", encoding="utf-8") as f:
        return f.read()


class TestHTMLParserInbox:
    """Tests for HTMLParser.parse_inbox_page()."""

    def test_parse_real_inbox_html(self, sample_inbox_real_html: str) -> None:
        """Test parsing real inbox HTML from LiveJournal."""
        messages, has_next_page = HTMLParser.parse_inbox_page(sample_inbox_real_html)

        # Should have parsed message(s)
        assert len(messages) > 0
        assert has_next_page is False  # Real sample is page 1 of 1

        # Verify first message structure
        message = messages[0]
        assert message.qid == 8
        assert message.msgid == 95201687
        assert message.type == "official_message"
        assert message.title == "LiveJournal User Agreement updated"
        assert "updated the LiveJournal User Agreement" in message.body
        assert message.timestamp_relative == "4 months ago"
        assert message.read is True
        assert message.bookmarked is False

    def test_parse_sender_verified_official(self, sample_inbox_real_html: str) -> None:
        """Test parsing sender info with verified badge."""
        messages, _ = HTMLParser.parse_inbox_page(sample_inbox_real_html)

        message = messages[0]
        assert message.sender is not None
        assert message.sender.username == "livejournal"
        assert message.sender.display_name == "livejournal"
        assert message.sender.verified is True
        assert "livejournal.com/profile" in message.sender.profile_url
        assert message.sender.userpic_url is not None

    def test_parse_empty_inbox(self, sample_inbox_empty_html: str) -> None:
        """Test parsing empty inbox page."""
        messages, has_next_page = HTMLParser.parse_inbox_page(sample_inbox_empty_html)

        assert len(messages) == 0
        assert messages == []
        assert has_next_page is False

    def test_parse_multipage_inbox(self, sample_inbox_multipage_html: str) -> None:
        """Test parsing inbox with multiple pages."""
        messages, has_next_page = HTMLParser.parse_inbox_page(sample_inbox_multipage_html)

        # Should have messages
        assert len(messages) == 1
        # Should indicate more pages exist
        assert has_next_page is True

        # Verify message
        message = messages[0]
        assert message.qid == 100
        assert message.msgid == 200

    def test_parse_pagination_single_page(self, sample_inbox_empty_html: str) -> None:
        """Test pagination extraction for single page."""
        messages, has_next_page = HTMLParser.parse_inbox_page(sample_inbox_empty_html)

        assert has_next_page is False

    def test_parse_pagination_multipage(self, sample_inbox_multipage_html: str) -> None:
        """Test pagination extraction for multiple pages."""
        messages, has_next_page = HTMLParser.parse_inbox_page(sample_inbox_multipage_html)

        # Page 2 of 5, so there should be more pages
        assert has_next_page is True

    def test_parse_message_read_status(self, sample_inbox_real_html: str) -> None:
        """Test that read status is correctly detected."""
        messages, _ = HTMLParser.parse_inbox_page(sample_inbox_real_html)

        # Real sample has read message
        assert messages[0].read is True

    def test_parse_message_bookmark_status(self, sample_inbox_real_html: str) -> None:
        """Test that bookmark status is correctly detected."""
        messages, _ = HTMLParser.parse_inbox_page(sample_inbox_real_html)

        # Real sample has unbookmarked message (flag_off.gif)
        assert messages[0].bookmarked is False

    def test_parse_message_qid(self, sample_inbox_real_html: str) -> None:
        """Test that qid is correctly extracted."""
        messages, _ = HTMLParser.parse_inbox_page(sample_inbox_real_html)

        assert messages[0].qid == 8

    def test_parse_message_msgid(self, sample_inbox_real_html: str) -> None:
        """Test that msgid is correctly extracted from reply link."""
        messages, _ = HTMLParser.parse_inbox_page(sample_inbox_real_html)

        assert messages[0].msgid == 95201687

    def test_parse_message_type_official(self, sample_inbox_real_html: str) -> None:
        """Test that official messages are correctly identified."""
        messages, _ = HTMLParser.parse_inbox_page(sample_inbox_real_html)

        # Real sample is from livejournal with verified badge
        assert messages[0].type == "official_message"

    def test_parse_message_body_extraction(self, sample_inbox_real_html: str) -> None:
        """Test that message body is correctly extracted without actions div."""
        messages, _ = HTMLParser.parse_inbox_page(sample_inbox_real_html)

        body = messages[0].body
        # Should contain the actual message
        assert "updated the LiveJournal User Agreement" in body
        # Should NOT contain the actions links
        assert "Reply" not in body
        assert "Mark as Spam" not in body

    def test_parse_invalid_html(self) -> None:
        """Test parsing malformed HTML raises ParsingError."""
        invalid_html = "<html><body><div>Invalid"

        # Should not raise - BeautifulSoup is tolerant
        messages, has_next = HTMLParser.parse_inbox_page(invalid_html)
        # But should return empty list
        assert len(messages) == 0


class TestHTMLParserPagination:
    """Tests for HTMLParser._extract_pagination()."""

    def test_extract_pagination_single_page(self) -> None:
        """Test extracting pagination for single page."""
        from bs4 import BeautifulSoup

        html = '<span class="page-number">Page 1 of 1</span>'
        soup = BeautifulSoup(html, "html.parser")

        current, total = HTMLParser._extract_pagination(soup)
        assert current == 1
        assert total == 1

    def test_extract_pagination_multipage(self) -> None:
        """Test extracting pagination for multiple pages."""
        from bs4 import BeautifulSoup

        html = '<span class="page-number">Page 3 of 10</span>'
        soup = BeautifulSoup(html, "html.parser")

        current, total = HTMLParser._extract_pagination(soup)
        assert current == 3
        assert total == 10

    def test_extract_pagination_missing(self) -> None:
        """Test extracting pagination when element is missing."""
        from bs4 import BeautifulSoup

        html = "<div>No pagination here</div>"
        soup = BeautifulSoup(html, "html.parser")

        with pytest.raises(ParsingError, match="Pagination info not found"):
            HTMLParser._extract_pagination(soup)

    def test_extract_pagination_invalid_format(self) -> None:
        """Test extracting pagination with invalid format."""
        from bs4 import BeautifulSoup

        html = '<span class="page-number">Invalid pagination text</span>'
        soup = BeautifulSoup(html, "html.parser")

        with pytest.raises(ParsingError, match="Could not parse pagination"):
            HTMLParser._extract_pagination(soup)


class TestHTMLParserMessageExtraction:
    """Tests for HTMLParser._extract_msgid()."""

    def test_extract_msgid_present(self) -> None:
        """Test extracting msgid when present."""
        from bs4 import BeautifulSoup

        html = """
        <tr class="InboxItem_Row">
            <td>
                <div class="actions">
                    <a href="https://www.livejournal.com/inbox/compose.bml?mode=reply&msgid=12345">Reply</a>
                </div>
            </td>
        </tr>
        """
        soup = BeautifulSoup(html, "html.parser")
        row = soup.find("tr")

        msgid = HTMLParser._extract_msgid(row)
        assert msgid == 12345

    def test_extract_msgid_missing_actions(self) -> None:
        """Test extracting msgid when actions div is missing."""
        from bs4 import BeautifulSoup

        html = '<tr class="InboxItem_Row"><td>No actions</td></tr>'
        soup = BeautifulSoup(html, "html.parser")
        row = soup.find("tr")

        msgid = HTMLParser._extract_msgid(row)
        assert msgid is None

    def test_extract_msgid_missing_reply_link(self) -> None:
        """Test extracting msgid when reply link is missing."""
        from bs4 import BeautifulSoup

        html = """
        <tr class="InboxItem_Row">
            <td>
                <div class="actions">
                    <a href="https://www.livejournal.com/other.bml">Other</a>
                </div>
            </td>
        </tr>
        """
        soup = BeautifulSoup(html, "html.parser")
        row = soup.find("tr")

        msgid = HTMLParser._extract_msgid(row)
        assert msgid is None


class TestHTMLParserSenderExtraction:
    """Tests for HTMLParser._extract_sender()."""

    def test_extract_sender_with_verified_badge(self) -> None:
        """Test extracting sender with verified badge."""
        from bs4 import BeautifulSoup

        html = """
        <span class="InboxItem_Title">
            Test message from
            <span class="ljuser" data-ljuser="testuser">
                <a href="https://testuser.livejournal.com/profile/" class="i-ljuser-profile">
                    <img class="i-ljuser-userhead" src="https://example.com/userpic.jpg" />
                </a>
                <a href="https://testuser.livejournal.com/"><b>testuser</b></a>
                <a class="i-ljuser-badge i-ljuser-badge--verified" data-badge-type="verified"></a>
            </span>
        </span>
        """
        soup = BeautifulSoup(html, "html.parser")
        title_span = soup.find("span", class_="InboxItem_Title")

        sender = HTMLParser._extract_sender(title_span)
        assert sender is not None
        assert sender.username == "testuser"
        assert sender.display_name == "testuser"
        assert sender.verified is True
        assert "testuser.livejournal.com/profile" in sender.profile_url
        assert sender.userpic_url == "https://example.com/userpic.jpg"

    def test_extract_sender_without_verified_badge(self) -> None:
        """Test extracting sender without verified badge."""
        from bs4 import BeautifulSoup

        html = """
        <span class="InboxItem_Title">
            <span class="ljuser" data-ljuser="normaluser">
                <a href="https://normaluser.livejournal.com/"><b>normaluser</b></a>
            </span>
        </span>
        """
        soup = BeautifulSoup(html, "html.parser")
        title_span = soup.find("span", class_="InboxItem_Title")

        sender = HTMLParser._extract_sender(title_span)
        assert sender is not None
        assert sender.username == "normaluser"
        assert sender.verified is False

    def test_extract_sender_missing_ljuser(self) -> None:
        """Test extracting sender when ljuser span is missing (system message)."""
        from bs4 import BeautifulSoup

        html = '<span class="InboxItem_Title">System notification</span>'
        soup = BeautifulSoup(html, "html.parser")
        title_span = soup.find("span", class_="InboxItem_Title")

        sender = HTMLParser._extract_sender(title_span)
        assert sender is None

    def test_extract_sender_missing_username(self) -> None:
        """Test extracting sender when username attribute is missing."""
        from bs4 import BeautifulSoup

        html = """
        <span class="InboxItem_Title">
            <span class="ljuser">
                <a href="https://example.com/"><b>someuser</b></a>
            </span>
        </span>
        """
        soup = BeautifulSoup(html, "html.parser")
        title_span = soup.find("span", class_="InboxItem_Title")

        sender = HTMLParser._extract_sender(title_span)
        assert sender is None
