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


@pytest.fixture
def sample_comment_meta_xml(fixtures_dir: Path) -> str:
    """Load sample comment metadata XML."""
    with open(fixtures_dir / "sample_comment_meta.xml") as f:
        return f.read()


@pytest.fixture
def sample_comment_meta_empty_xml(fixtures_dir: Path) -> str:
    """Load empty comment metadata XML."""
    with open(fixtures_dir / "sample_comment_meta_empty.xml") as f:
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
        assert post1.jitemid == 457
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
        assert post2.jitemid == 458
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
        assert post.jitemid == 456
        assert post.subject == "Simple Post"

    def test_jitemid_present(self, sample_posts_xml: str) -> None:
        """Test that jitemid is present in parsed posts."""
        posts = XMLParser.parse_posts(sample_posts_xml)

        for post in posts:
            # Verify jitemid is set (exact value from XML)
            assert post.jitemid is not None

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


class TestXMLParserCommentMetadata:
    """Tests for XMLParser.parse_comment_metadata()."""

    def test_parse_comment_metadata(self, sample_comment_meta_xml: str) -> None:
        """Test parsing comment metadata from XML."""
        maxid, usermap = XMLParser.parse_comment_metadata(sample_comment_meta_xml)

        # Verify maxid
        assert maxid == 987654

        # Verify usermap
        assert len(usermap) == 4

        # Verify first user
        user1 = usermap[0]
        assert user1.userid == 123
        assert user1.username == "friend1"

        # Verify second user
        user2 = usermap[1]
        assert user2.userid == 456
        assert user2.username == "friend2"

        # Verify third user
        user3 = usermap[2]
        assert user3.userid == 789
        assert user3.username == "testuser"

        # Verify fourth user
        user4 = usermap[3]
        assert user4.userid == 1001
        assert user4.username == "anonymous_coward"

    def test_parse_comment_metadata_empty_usermap(self, sample_comment_meta_empty_xml: str) -> None:
        """Test parsing comment metadata with no users."""
        maxid, usermap = XMLParser.parse_comment_metadata(sample_comment_meta_empty_xml)

        assert maxid == 0
        assert len(usermap) == 0
        assert usermap == []

    def test_parse_comment_metadata_invalid_xml(self) -> None:
        """Test parsing malformed XML raises ParsingError."""
        invalid_xml = "<livejournal><maxid>123</livejournal>"

        with pytest.raises(ParsingError, match="Failed to parse XML"):
            XMLParser.parse_comment_metadata(invalid_xml)

    def test_parse_comment_metadata_missing_maxid(self) -> None:
        """Test parsing XML without maxid raises ParsingError."""
        xml_without_maxid = """<?xml version="1.0"?>
<livejournal>
  <usermap id="123" user="test" />
</livejournal>
"""
        with pytest.raises(ParsingError, match="Missing required field: maxid"):
            XMLParser.parse_comment_metadata(xml_without_maxid)

    def test_parse_comment_metadata_invalid_maxid(self) -> None:
        """Test parsing XML with non-numeric maxid raises ParsingError."""
        xml_invalid_maxid = """<?xml version="1.0"?>
<livejournal>
  <maxid>not_a_number</maxid>
</livejournal>
"""
        with pytest.raises(ParsingError, match="Invalid maxid value"):
            XMLParser.parse_comment_metadata(xml_invalid_maxid)

    def test_parse_comment_metadata_malformed_usermap(self) -> None:
        """Test parsing with malformed usermap elements skips them."""
        xml_malformed_usermap = """<?xml version="1.0"?>
<livejournal>
  <maxid>100</maxid>
  <usermap id="123" user="valid_user" />
  <usermap user="missing_id" />
  <usermap id="456" />
  <usermap id="not_a_number" user="bad_id" />
  <usermap id="789" user="another_valid" />
</livejournal>
"""
        maxid, usermap = XMLParser.parse_comment_metadata(xml_malformed_usermap)

        # Should have parsed maxid and only valid usermaps
        assert maxid == 100
        assert len(usermap) == 2

        # Verify only valid users were parsed
        assert usermap[0].userid == 123
        assert usermap[0].username == "valid_user"
        assert usermap[1].userid == 789
        assert usermap[1].username == "another_valid"
