"""Tests for XML and HTML parsers."""

from pathlib import Path

import pytest

from yalje.core.exceptions import ParsingError
from yalje.parsers.xml_parser import XMLParser


@pytest.fixture
def fixtures_dir() -> Path:
    """Get the fixtures directory path."""
    return Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def sample_posts_xml(fixtures_dir: Path) -> str:
    """Load sample posts XML."""
    with open(fixtures_dir / "sample_posts.xml") as f:
        return f.read()


@pytest.fixture
def sample_posts_empty_xml(fixtures_dir: Path) -> str:
    """Load empty posts XML."""
    with open(fixtures_dir / "sample_posts_empty.xml") as f:
        return f.read()


@pytest.fixture
def sample_posts_single_xml(fixtures_dir: Path) -> str:
    """Load single post XML."""
    with open(fixtures_dir / "sample_posts_single.xml") as f:
        return f.read()


class TestXMLParserPosts:
    """Tests for XMLParser.parse_posts()."""

    def test_parse_multiple_posts(self, sample_posts_xml: str) -> None:
        """Test parsing multiple posts from XML."""
        posts = XMLParser.parse_posts(sample_posts_xml)

        # Should have 4 posts
        assert len(posts) == 4

        # Verify first post
        post1 = posts[0]
        assert post1.itemid == 116992
        assert post1.jitemid == 457  # 116992 >> 8
        assert post1.subject == "First Post Title"
        assert post1.event == "<p>This is the <b>first post</b> with HTML content.</p>"
        assert post1.security == "public"
        assert post1.allowmask == 0
        assert post1.current_mood == "happy"
        assert post1.current_music == "Artist - Song Title"
        assert post1.eventtime == "2023-01-15 14:30:00"
        assert post1.logtime == "2023-01-15 14:30:00"

        # Verify post without subject (empty string should be None)
        post2 = posts[1]
        assert post2.itemid == 117248
        assert post2.jitemid == 458  # 117248 >> 8
        assert post2.subject is None
        assert post2.security == "private"
        assert post2.current_mood is None
        assert post2.current_music is None

        # Verify friends-only post
        post3 = posts[2]
        assert post3.itemid == 117504
        assert post3.security == "friends"
        assert post3.current_mood == "contemplative"

        # Verify custom security post
        post4 = posts[3]
        assert post4.itemid == 117760
        assert post4.security == "custom"
        assert post4.allowmask == 42

    def test_parse_empty_xml(self, sample_posts_empty_xml: str) -> None:
        """Test parsing XML with no posts."""
        posts = XMLParser.parse_posts(sample_posts_empty_xml)
        assert len(posts) == 0
        assert posts == []

    def test_parse_single_post(self, sample_posts_single_xml: str) -> None:
        """Test parsing single post."""
        posts = XMLParser.parse_posts(sample_posts_single_xml)
        assert len(posts) == 1

        post = posts[0]
        assert post.itemid == 116736
        assert post.jitemid == 456  # 116736 >> 8
        assert post.subject == "Simple Post"

    def test_jitemid_calculation(self, sample_posts_xml: str) -> None:
        """Test that jitemid is calculated correctly."""
        posts = XMLParser.parse_posts(sample_posts_xml)

        for post in posts:
            # Verify jitemid matches itemid >> 8
            assert post.jitemid == (post.itemid >> 8)

    def test_cdata_handling(self, sample_posts_xml: str) -> None:
        """Test that CDATA sections are handled correctly."""
        posts = XMLParser.parse_posts(sample_posts_xml)

        # First post has HTML with bold tag
        assert "<b>first post</b>" in posts[0].event
        # Multiple paragraphs in post 3
        assert "<p>Multiple paragraphs!</p>" in posts[2].event

    def test_invalid_xml(self) -> None:
        """Test parsing malformed XML raises ParsingError."""
        invalid_xml = "<livejournal><entry>Invalid</livejournal>"

        with pytest.raises(ParsingError, match="Failed to parse XML"):
            XMLParser.parse_posts(invalid_xml)

    def test_missing_required_field_itemid(self) -> None:
        """Test parsing entry without itemid raises ParsingError."""
        xml_without_itemid = """<?xml version="1.0"?>
<livejournal>
  <entry>
    <eventtime>2023-01-15 14:30:00</eventtime>
    <logtime>2023-01-15 14:30:00</logtime>
    <subject>Test</subject>
    <event><![CDATA[Content]]></event>
    <security>public</security>
  </entry>
</livejournal>
"""
        with pytest.raises(ParsingError, match="Missing required field: itemid"):
            XMLParser.parse_posts(xml_without_itemid)

    def test_missing_required_field_security(self) -> None:
        """Test parsing entry without security raises ParsingError."""
        xml_without_security = """<?xml version="1.0"?>
<livejournal>
  <entry>
    <itemid>12345</itemid>
    <eventtime>2023-01-15 14:30:00</eventtime>
    <logtime>2023-01-15 14:30:00</logtime>
    <subject>Test</subject>
    <event><![CDATA[Content]]></event>
  </entry>
</livejournal>
"""
        with pytest.raises(ParsingError, match="Missing required field: security"):
            XMLParser.parse_posts(xml_without_security)

    def test_optional_fields_default_values(self) -> None:
        """Test that optional fields have correct default values."""
        xml_minimal = """<?xml version="1.0"?>
<livejournal>
  <entry>
    <itemid>12345</itemid>
    <eventtime>2023-01-15 14:30:00</eventtime>
    <logtime>2023-01-15 14:30:00</logtime>
    <event><![CDATA[Content]]></event>
    <security>public</security>
  </entry>
</livejournal>
"""
        posts = XMLParser.parse_posts(xml_minimal)
        assert len(posts) == 1

        post = posts[0]
        assert post.subject is None
        assert post.allowmask == 0
        assert post.current_mood is None
        assert post.current_music is None
