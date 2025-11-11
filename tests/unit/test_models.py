"""Tests for data models."""

from yalje.models.export import LJExport
from yalje.models.post import Post


def test_post_jitemid_calculation():
    """Test that jitemid is calculated correctly from itemid."""
    # Test with explicit jitemid (116736 >> 8 = 456)
    post = Post(
        itemid=116736,
        jitemid=456,
        eventtime="2023-01-15 14:30:00",
        logtime="2023-01-15 14:30:00",
        subject="Test",
        event="Content",
        security="public",
    )
    assert post.jitemid == 456
    assert post.jitemid == (post.itemid >> 8)

    # Test automatic calculation when jitemid not provided
    post2 = Post(
        itemid=116736,
        eventtime="2023-01-15 14:30:00",
        logtime="2023-01-15 14:30:00",
        subject="Test",
        event="Content",
        security="public",
    )
    assert post2.jitemid == 456
    assert post2.jitemid == (post2.itemid >> 8)


def test_export_serialization(sample_export):
    """Test export can be serialized to YAML and back."""
    # Serialize to YAML
    yaml_str = sample_export.to_yaml()
    assert "metadata" in yaml_str
    assert "lj_user: testuser" in yaml_str

    # Deserialize from YAML
    loaded = LJExport.from_yaml(yaml_str)
    assert loaded.metadata.lj_user == "testuser"
