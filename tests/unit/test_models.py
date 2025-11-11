"""Tests for data models."""

from yalje.models.export import LJExport
from yalje.models.post import Post


def test_post_jitemid_calculation():
    """Test that jitemid is calculated correctly from itemid."""
    post = Post(
        itemid=116992,
        jitemid=456,  # Should equal 116992 >> 8
        eventtime="2023-01-15 14:30:00",
        logtime="2023-01-15 14:30:00",
        subject="Test",
        event="Content",
        security="public",
    )
    assert post.jitemid == 456
    assert post.jitemid == (post.itemid >> 8)


def test_export_serialization(sample_export):
    """Test export can be serialized to YAML and back."""
    # Serialize to YAML
    yaml_str = sample_export.to_yaml()
    assert "metadata" in yaml_str
    assert "lj_user: testuser" in yaml_str

    # Deserialize from YAML
    loaded = LJExport.from_yaml(yaml_str)
    assert loaded.metadata.lj_user == "testuser"
