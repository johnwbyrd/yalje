"""Tests for exporters (YAML, JSON, XML)."""

import tempfile
from pathlib import Path

import pytest

from yalje.exporters.json_exporter import JSONExporter
from yalje.exporters.xml_exporter import XMLExporter
from yalje.exporters.yaml_exporter import YAMLExporter
from yalje.models.comment import Comment
from yalje.models.export import ExportMetadata, LJExport
from yalje.models.inbox import InboxMessage
from yalje.models.post import Post
from yalje.models.user import InboxSender, User


@pytest.fixture
def sample_export():
    """Create a sample LJExport object for testing."""
    metadata = ExportMetadata(
        export_date="2025-11-11T00:00:00Z",
        lj_user="testuser",
        yalje_version="0.1.0",
        post_count=2,
        comment_count=1,
        inbox_count=1,
    )

    usermap = [
        User(userid=123, username="friend1"),
        User(userid=456, username="friend2"),
    ]

    posts = [
        Post(
            itemid=1,
            jitemid=100,
            eventtime="2023-01-01 12:00:00",
            logtime="2023-01-01 12:00:00",
            subject="Test Post",
            event="<p>Test content with <b>HTML</b></p>",
            security="public",
            allowmask=0,
            current_mood="happy",
            current_music="Test Song",
        ),
        Post(
            itemid=2,
            jitemid=None,
            eventtime="2023-01-02 12:00:00",
            logtime="2023-01-02 12:00:00",
            subject=None,
            event="No subject post",
            security="private",
            allowmask=0,
            current_mood=None,
            current_music=None,
        ),
    ]

    comments = [
        Comment(
            id=1,
            jitemid=100,
            posterid=123,
            poster_username="friend1",
            parentid=None,
            date="2023-01-01 13:00:00",
            subject="Re: Test Post",
            body="<p>Test comment</p>",
            state=None,
        ),
    ]

    inbox = [
        InboxMessage(
            qid=239,
            msgid=95534705,
            type="official_message",
            sender=InboxSender(
                username="livejournal",
                display_name="LiveJournal",
                profile_url="https://livejournal.livejournal.com/profile/",
                userpic_url="https://example.com/pic.jpg",
                verified=True,
            ),
            title="Test Message",
            body="Test body",
            timestamp_relative="1 day ago",
            timestamp_absolute=None,
            read=False,
            bookmarked=False,
        ),
    ]

    return LJExport(
        metadata=metadata,
        usermap=usermap,
        posts=posts,
        comments=comments,
        inbox=inbox,
    )


class TestYAMLExporter:
    """Tests for YAMLExporter."""

    def test_export_and_load(self, sample_export):
        """Test export to YAML and load back."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.yaml"
            exporter = YAMLExporter()

            # Export
            exporter.export(sample_export, output_path)
            assert output_path.exists()

            # Load
            loaded = exporter.load(output_path)
            assert loaded.metadata.lj_user == sample_export.metadata.lj_user
            assert len(loaded.posts) == len(sample_export.posts)
            assert len(loaded.comments) == len(sample_export.comments)
            assert len(loaded.inbox) == len(sample_export.inbox)


class TestJSONExporter:
    """Tests for JSONExporter."""

    def test_export_and_load(self, sample_export):
        """Test export to JSON and load back."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.json"
            exporter = JSONExporter()

            # Export
            exporter.export(sample_export, output_path)
            assert output_path.exists()

            # Load
            loaded = exporter.load(output_path)
            assert loaded.metadata.lj_user == sample_export.metadata.lj_user
            assert len(loaded.posts) == len(sample_export.posts)
            assert len(loaded.comments) == len(sample_export.comments)
            assert len(loaded.inbox) == len(sample_export.inbox)

    def test_export_string(self, sample_export):
        """Test export to JSON string."""
        exporter = JSONExporter()
        json_str = exporter.export_string(sample_export)

        assert "testuser" in json_str
        assert "Test Post" in json_str
        assert isinstance(json_str, str)


class TestXMLExporter:
    """Tests for XMLExporter."""

    def test_export_and_load(self, sample_export):
        """Test export to XML and load back."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.xml"
            exporter = XMLExporter()

            # Export
            exporter.export(sample_export, output_path)
            assert output_path.exists()

            # Load
            loaded = exporter.load(output_path)
            assert loaded.metadata.lj_user == sample_export.metadata.lj_user
            assert len(loaded.posts) == len(sample_export.posts)
            assert len(loaded.comments) == len(sample_export.comments)
            assert len(loaded.inbox) == len(sample_export.inbox)

    def test_export_string(self, sample_export):
        """Test export to XML string."""
        exporter = XMLExporter()
        xml_str = exporter.export_string(sample_export)

        assert '<?xml version="1.0" encoding="UTF-8"?>' in xml_str
        assert "<lj_export>" in xml_str
        assert "<metadata>" in xml_str
        assert "<lj_user>testuser</lj_user>" in xml_str
        assert isinstance(xml_str, str)

    def test_xml_structure(self, sample_export):
        """Test XML structure contains all expected elements."""
        exporter = XMLExporter()
        xml_str = exporter.export_string(sample_export)

        # Check for major sections
        assert "<metadata>" in xml_str
        assert "<usermap>" in xml_str
        assert "<posts>" in xml_str
        assert "<comments>" in xml_str
        assert "<inbox>" in xml_str

        # Check metadata fields
        assert "<export_date>" in xml_str
        assert "<yalje_version>" in xml_str
        assert "<post_count>" in xml_str

        # Check post structure
        assert "<post>" in xml_str
        assert "<itemid>" in xml_str
        assert "<subject>Test Post</subject>" in xml_str
        assert "<event>" in xml_str

        # Check comment structure
        assert "<comment>" in xml_str
        assert "<posterid>" in xml_str

        # Check inbox structure
        assert "<message>" in xml_str
        assert "<qid>" in xml_str
        assert "<sender>" in xml_str

    def test_xml_handles_none_values(self, sample_export):
        """Test that XML properly handles None/null values."""
        exporter = XMLExporter()

        # Post with jitemid=None should have empty tag or handle it gracefully
        # The second post has jitemid=None
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.xml"
            exporter.export(sample_export, output_path)

            # Load back and verify
            loaded = exporter.load(output_path)
            assert loaded.posts[1].jitemid is None
            assert loaded.posts[1].subject is None
            assert loaded.comments[0].parentid is None

    def test_xml_handles_html_content(self, sample_export):
        """Test that XML properly handles HTML content."""
        exporter = XMLExporter()
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.xml"
            exporter.export(sample_export, output_path)

            # Load back and verify HTML is preserved
            loaded = exporter.load(output_path)
            assert "<b>HTML</b>" in loaded.posts[0].event
            assert "<p>Test comment</p>" in loaded.comments[0].body


class TestExporterComparison:
    """Tests to ensure all exporters produce equivalent output."""

    def test_round_trip_equivalence(self, sample_export):
        """Test that all exporters preserve data through round-trip."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / "test.yaml"
            json_path = Path(tmpdir) / "test.json"
            xml_path = Path(tmpdir) / "test.xml"

            # Export to all formats
            YAMLExporter().export(sample_export, yaml_path)
            JSONExporter().export(sample_export, json_path)
            XMLExporter().export(sample_export, xml_path)

            # Load from all formats
            yaml_loaded = YAMLExporter.load(yaml_path)
            json_loaded = JSONExporter.load(json_path)
            xml_loaded = XMLExporter.load(xml_path)

            # Verify all have same data
            assert yaml_loaded.metadata.lj_user == json_loaded.metadata.lj_user
            assert json_loaded.metadata.lj_user == xml_loaded.metadata.lj_user

            assert len(yaml_loaded.posts) == len(json_loaded.posts)
            assert len(json_loaded.posts) == len(xml_loaded.posts)

            assert yaml_loaded.posts[0].subject == json_loaded.posts[0].subject
            assert json_loaded.posts[0].subject == xml_loaded.posts[0].subject
