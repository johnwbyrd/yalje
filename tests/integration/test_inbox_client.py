"""Integration tests for InboxClient."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests

from yalje.api.inbox import InboxClient
from yalje.core.config import YaljeConfig
from yalje.core.exceptions import APIError
from yalje.core.session import HTTPSession


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


class TestInboxClient:
    """Tests for InboxClient."""

    def test_download_page_success(
        self,
        mock_session: HTTPSession,
        mock_config: YaljeConfig,
        sample_inbox_real_html: str,
        mocker,
    ) -> None:
        """Test successful inbox page download."""
        # Mock the session.get method
        mock_response = MagicMock(spec=requests.Response)
        mock_response.text = sample_inbox_real_html
        mock_response.status_code = 200
        mocker.patch.object(mock_session, "get", return_value=mock_response)

        # Create client and download
        client = InboxClient(mock_session, mock_config)
        messages, has_next = client.download_page("all", 1)

        # Verify results
        assert len(messages) > 0
        assert has_next is False
        assert messages[0].qid == 8
        assert messages[0].msgid == 95201687

        # Verify the request was made correctly
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args

        # Check URL
        assert call_args[0][0] == "https://www.livejournal.com/inbox/"

        # Check params
        params = call_args[1]["params"]
        assert params["view"] == "all"
        assert params["page"] == "1"

    def test_download_page_empty(
        self,
        mock_session: HTTPSession,
        mock_config: YaljeConfig,
        sample_inbox_empty_html: str,
        mocker,
    ) -> None:
        """Test downloading an empty inbox page."""
        # Mock the session.get method
        mock_response = MagicMock(spec=requests.Response)
        mock_response.text = sample_inbox_empty_html
        mock_response.status_code = 200
        mocker.patch.object(mock_session, "get", return_value=mock_response)

        # Create client and download
        client = InboxClient(mock_session, mock_config)
        messages, has_next = client.download_page("all", 1)

        # Should return empty list
        assert len(messages) == 0
        assert messages == []
        assert has_next is False

    def test_download_page_multipage(
        self,
        mock_session: HTTPSession,
        mock_config: YaljeConfig,
        sample_inbox_multipage_html: str,
        mocker,
    ) -> None:
        """Test downloading page with more pages available."""
        # Mock the session.get method
        mock_response = MagicMock(spec=requests.Response)
        mock_response.text = sample_inbox_multipage_html
        mock_response.status_code = 200
        mocker.patch.object(mock_session, "get", return_value=mock_response)

        # Create client and download
        client = InboxClient(mock_session, mock_config)
        messages, has_next = client.download_page("all", 2)

        # Should have messages and indicate more pages
        assert len(messages) == 1
        assert has_next is True

    def test_download_page_api_error(
        self, mock_session: HTTPSession, mock_config: YaljeConfig, mocker
    ) -> None:
        """Test handling of API errors."""
        # Mock the session.get to raise an exception
        mocker.patch.object(mock_session, "get", side_effect=APIError("Network error"))

        # Create client and attempt download
        client = InboxClient(mock_session, mock_config)

        with pytest.raises(APIError, match="Network error"):
            client.download_page("all", 1)

    def test_download_folder_single_page(
        self,
        mock_session: HTTPSession,
        mock_config: YaljeConfig,
        sample_inbox_real_html: str,
        mocker,
    ) -> None:
        """Test downloading folder with single page."""
        # Mock the session.get method
        mock_response = MagicMock(spec=requests.Response)
        mock_response.text = sample_inbox_real_html
        mock_response.status_code = 200
        mocker.patch.object(mock_session, "get", return_value=mock_response)

        # Create client and download
        client = InboxClient(mock_session, mock_config)
        messages = client.download_folder("all")

        # Should call get once (single page)
        assert mock_session.get.call_count == 1

        # Should have messages
        assert len(messages) > 0

    def test_download_folder_multiple_pages(
        self,
        mock_session: HTTPSession,
        mock_config: YaljeConfig,
        sample_inbox_multipage_html: str,
        sample_inbox_real_html: str,
        mocker,
    ) -> None:
        """Test downloading folder with multiple pages."""

        # Mock the session.get method to return different pages
        def mock_get_side_effect(url, params=None):
            mock_response = MagicMock(spec=requests.Response)
            # First 4 pages return multipage HTML, last page returns single page
            if params and int(params.get("page", "1")) < 5:
                mock_response.text = sample_inbox_multipage_html
            else:
                mock_response.text = sample_inbox_real_html
            mock_response.status_code = 200
            return mock_response

        mocker.patch.object(mock_session, "get", side_effect=mock_get_side_effect)

        # Create client and download
        client = InboxClient(mock_session, mock_config)
        messages = client.download_folder("all")

        # Should call get multiple times (5 pages)
        assert mock_session.get.call_count == 5

        # Should have messages from all pages
        assert len(messages) == 5  # 1 message per page

    def test_download_all_single_folder(
        self,
        mock_session: HTTPSession,
        mock_config: YaljeConfig,
        sample_inbox_real_html: str,
        mocker,
    ) -> None:
        """Test downloading all folders (default single folder)."""
        # Mock the session.get method
        mock_response = MagicMock(spec=requests.Response)
        mock_response.text = sample_inbox_real_html
        mock_response.status_code = 200
        mocker.patch.object(mock_session, "get", return_value=mock_response)

        # Create client and download
        client = InboxClient(mock_session, mock_config)
        messages = client.download_all()

        # Should download default folder
        assert len(messages) > 0

    def test_download_all_multiple_folders(
        self,
        mock_session: HTTPSession,
        mock_config: YaljeConfig,
        sample_inbox_real_html: str,
        mocker,
    ) -> None:
        """Test downloading multiple folders."""
        # Mock the session.get method
        mock_response = MagicMock(spec=requests.Response)
        mock_response.text = sample_inbox_real_html
        mock_response.status_code = 200
        mocker.patch.object(mock_session, "get", return_value=mock_response)

        # Create client and download
        client = InboxClient(mock_session, mock_config)
        messages = client.download_all(folders=["all", "usermsg_recvd"])

        # Should call get twice (once per folder)
        assert mock_session.get.call_count == 2

        # Should have messages from both folders
        assert len(messages) > 0

    def test_download_folder_with_view_parameter(
        self,
        mock_session: HTTPSession,
        mock_config: YaljeConfig,
        sample_inbox_real_html: str,
        mocker,
    ) -> None:
        """Test that view parameter is correctly passed."""
        # Mock the session.get method
        mock_response = MagicMock(spec=requests.Response)
        mock_response.text = sample_inbox_real_html
        mock_response.status_code = 200
        mocker.patch.object(mock_session, "get", return_value=mock_response)

        # Create client and download with specific view
        client = InboxClient(mock_session, mock_config)
        client.download_folder("usermsg_recvd")

        # Verify the view parameter was passed
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert params["view"] == "usermsg_recvd"
