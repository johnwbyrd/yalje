"""Pytest configuration and fixtures."""

import pytest

from yalje.core.config import YaljeConfig
from yalje.models.export import ExportMetadata, LJExport


@pytest.fixture
def sample_config() -> YaljeConfig:
    """Create a sample configuration for testing."""
    return YaljeConfig(
        username="testuser",
        base_url="https://www.livejournal.com",
        request_timeout=10,
    )


@pytest.fixture
def sample_export() -> LJExport:
    """Create a sample export object for testing."""
    metadata = ExportMetadata(
        lj_user="testuser",
        yalje_version="0.1.0",
    )
    return LJExport(metadata=metadata)
