"""Integration tests for API clients."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests

from yalje.api.posts import PostsClient
from yalje.core.config import YaljeConfig
from yalje.core.exceptions import APIError
from yalje.core.session import HTTPSession


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
def mock_config() -> YaljeConfig:
    """Create a mock configuration."""
    return YaljeConfig(
        username="testuser",
        base_url="https://www.livejournal.com",
        request_timeout=10,
        request_delay=0.0,  # No delay in tests
    )


@pytest.fixture
def mock_session(mock_config: YaljeConfig) -> HTTPSession:
    """Create a mock HTTP session."""
    return HTTPSession(mock_config)


class TestPostsClient:
    """Tests for PostsClient."""

    def test_download_month_success(
        self, mock_session: HTTPSession, mock_config: YaljeConfig, sample_posts_xml: str, mocker
    ) -> None:
        """Test successful month download."""
        # Mock the session.post method
        mock_response = MagicMock(spec=requests.Response)
        mock_response.text = sample_posts_xml
        mock_response.status_code = 200
        mocker.patch.object(mock_session, "post", return_value=mock_response)

        # Create client and download
        client = PostsClient(mock_session, mock_config)
        posts = client.download_month(2023, 1)

        # Verify results
        assert len(posts) == 4
        assert posts[0].itemid == 116992
        assert posts[0].subject == "First Post Title"

        # Verify the request was made correctly
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args

        # Check URL
        assert call_args[0][0] == "https://www.livejournal.com/export_do.bml"

        # Check data parameters
        data = call_args[1]["data"]
        assert data["what"] == "journal"
        assert data["year"] == "2023"
        assert data["month"] == "01"  # Zero-padded
        assert data["format"] == "xml"
        assert data["encid"] == "2"

    def test_download_month_empty(
        self,
        mock_session: HTTPSession,
        mock_config: YaljeConfig,
        sample_posts_empty_xml: str,
        mocker,
    ) -> None:
        """Test downloading an empty month."""
        # Mock the session.post method
        mock_response = MagicMock(spec=requests.Response)
        mock_response.text = sample_posts_empty_xml
        mock_response.status_code = 200
        mocker.patch.object(mock_session, "post", return_value=mock_response)

        # Create client and download
        client = PostsClient(mock_session, mock_config)
        posts = client.download_month(2023, 5)

        # Should return empty list
        assert len(posts) == 0
        assert posts == []

    def test_download_month_zero_padded(
        self, mock_session: HTTPSession, mock_config: YaljeConfig, sample_posts_xml: str, mocker
    ) -> None:
        """Test that month is zero-padded in request."""
        # Mock the session.post method
        mock_response = MagicMock(spec=requests.Response)
        mock_response.text = sample_posts_xml
        mock_response.status_code = 200
        mocker.patch.object(mock_session, "post", return_value=mock_response)

        # Create client and download month 3
        client = PostsClient(mock_session, mock_config)
        client.download_month(2023, 3)

        # Check that month was zero-padded
        call_args = mock_session.post.call_args
        data = call_args[1]["data"]
        assert data["month"] == "03"

    def test_download_month_api_error(
        self, mock_session: HTTPSession, mock_config: YaljeConfig, mocker
    ) -> None:
        """Test handling of API errors."""
        # Mock the session.post to raise an exception
        mocker.patch.object(mock_session, "post", side_effect=APIError("Network error"))

        # Create client and attempt download
        client = PostsClient(mock_session, mock_config)

        with pytest.raises(APIError, match="Network error"):
            client.download_month(2023, 1)

    def test_download_all_multiple_months(
        self, mock_session: HTTPSession, mock_config: YaljeConfig, sample_posts_xml: str, mocker
    ) -> None:
        """Test downloading multiple months."""
        # Mock the session.post method
        mock_response = MagicMock(spec=requests.Response)
        mock_response.text = sample_posts_xml
        mock_response.status_code = 200
        mocker.patch.object(mock_session, "post", return_value=mock_response)

        # Create client and download range
        client = PostsClient(mock_session, mock_config)
        posts = client.download_all(2023, 1, 2023, 3)  # Jan-Mar 2023

        # Should call download_month 3 times
        assert mock_session.post.call_count == 3

        # Should have 12 posts (4 per month × 3 months)
        assert len(posts) == 12

    def test_month_range_generation(
        self, mock_session: HTTPSession, mock_config: YaljeConfig
    ) -> None:
        """Test month range generation."""
        client = PostsClient(mock_session, mock_config)

        # Test single month
        months = list(client._generate_month_range(2023, 1, 2023, 1))
        assert months == [(2023, 1)]

        # Test multiple months in same year
        months = list(client._generate_month_range(2023, 1, 2023, 3))
        assert months == [(2023, 1), (2023, 2), (2023, 3)]

        # Test across year boundary
        months = list(client._generate_month_range(2022, 11, 2023, 2))
        assert months == [(2022, 11), (2022, 12), (2023, 1), (2023, 2)]

        # Test full year
        months = list(client._generate_month_range(2023, 1, 2023, 12))
        assert len(months) == 12
