"""
Tests for the SefariaClient class.
"""

import json
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from requests.exceptions import HTTPError, RequestException

from sefaria_sdk.client import SefariaClient


class TestSefariaClient:
    """Test cases for SefariaClient."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = SefariaClient()

    def test_init_default_values(self):
        """Test client initialization with default values."""
        client = SefariaClient()
        assert client.base_url == "https://www.sefaria.org/api"
        assert "Unofficial-Sefaria-Python-SDK" in client.headers["User-Agent"]
        assert client.headers["Accept"] == "application/json"

    def test_init_custom_values(self):
        """Test client initialization with custom values."""
        custom_url = "https://custom.sefaria.org/api"
        custom_agent = "Custom-Agent/1.0"
        client = SefariaClient(base_url=custom_url, user_agent=custom_agent)

        assert client.base_url == custom_url
        assert client.headers["User-Agent"] == custom_agent

    def test_init_strips_trailing_slash(self):
        """Test that trailing slash is stripped from base URL."""
        client = SefariaClient(base_url="https://www.sefaria.org/api/")
        assert client.base_url == "https://www.sefaria.org/api"

    @patch("requests.Session.get")
    def test_get_text_success(self, mock_get):
        """Test successful text retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "versions": [{"text": ["In the beginning"]}],
            "ref": "Genesis 1:1",
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_text("Genesis 1:1")

        assert result["ref"] == "Genesis 1:1"
        mock_get.assert_called_once()

    @patch("requests.Session.get")
    def test_get_text_with_params(self, mock_get):
        """Test text retrieval with additional parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {"ref": "Genesis 1:1"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        self.client.get_text("Genesis 1:1", lang="en", version="JPS")

        args, kwargs = mock_get.call_args
        assert kwargs["params"]["lang"] == "en"
        assert kwargs["params"]["version"] == "JPS"

    @patch("requests.Session.get")
    def test_get_text_http_error(self, mock_get):
        """Test text retrieval with HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        with pytest.raises(HTTPError):
            self.client.get_text("Invalid Reference")

    @patch("requests.Session.post")
    def test_search_success(self, mock_post):
        """Test successful search."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "hits": {"total": 5, "hits": [{"_source": {"ref": "Genesis 1:1"}}]}
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.search("charity")

        assert result["hits"]["total"] == 5
        mock_post.assert_called_once()

    @patch("requests.Session.post")
    def test_search_with_params(self, mock_post):
        """Test search with additional parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {"hits": {"total": 0}}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        self.client.search("charity", limit=10, sort_type="relevance")

        args, kwargs = mock_post.call_args
        payload = kwargs["json"]
        assert payload["query"] == "charity"
        assert payload["size"] == 10
        assert payload["sort_type"] == "relevance"

    @patch("requests.Session.get")
    def test_get_related_success(self, mock_get):
        """Test successful related content retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {"links": [{"ref": "Rashi on Genesis 1:1"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_related("Genesis 1:1")

        assert len(result["links"]) == 1
        mock_get.assert_called_once()

    @patch("requests.Session.get")
    def test_get_languages_success(self, mock_get):
        """Test successful language retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "en": ["JPS 1917", "Robert Alter"],
            "he": ["Tanach with Text Only"],
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_languages()

        assert "en" in result
        assert "he" in result
        mock_get.assert_called_once()

    @patch("requests.Session.get")
    def test_get_calendar_success(self, mock_get):
        """Test successful calendar retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "calendar_items": [{"title": {"en": "Parashat Bereshit"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_calendar()

        assert "calendar_items" in result
        mock_get.assert_called_once()

    @patch("requests.Session.get")
    def test_retry_mechanism(self, mock_get):
        """Test that retry mechanism is configured."""
        # Verify that HTTPAdapter with retries is mounted
        assert "https://" in self.client.session.adapters
        assert "http://" in self.client.session.adapters

        adapter = self.client.session.adapters["https://"]
        assert hasattr(adapter, "max_retries")

    def test_url_encoding(self):
        """Test that URLs are properly encoded."""
        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            self.client.get_text("Genesis 1:1-5")

            args, kwargs = mock_get.call_args
            url = args[0]
            assert "Genesis%201%3A1-5" in url

    @patch("requests.Session.get")
    def test_timeout_configuration(self, mock_get):
        """Test that timeouts are properly configured."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        self.client.get_text("Genesis 1:1")

        args, kwargs = mock_get.call_args
        assert kwargs["timeout"] == 15

    @patch("requests.Session.post")
    def test_search_timeout_configuration(self, mock_post):
        """Test that search timeouts are properly configured."""
        mock_response = Mock()
        mock_response.json.return_value = {"hits": {"total": 0}}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        self.client.search("test")

        args, kwargs = mock_post.call_args
        assert kwargs["timeout"] == 20

    def test_headers_configuration(self):
        """Test that headers are properly configured."""
        assert self.client.headers["Accept"] == "application/json"
        assert "User-Agent" in self.client.headers

    @patch("requests.Session.get")
    def test_request_exception_handling(self, mock_get):
        """Test handling of request exceptions."""
        mock_get.side_effect = RequestException("Network error")

        with pytest.raises(RequestException):
            self.client.get_text("Genesis 1:1")

    @patch("requests.Session.post")
    def test_search_request_exception_handling(self, mock_post):
        """Test handling of search request exceptions."""
        mock_post.side_effect = RequestException("Network error")

        with pytest.raises(RequestException):
            self.client.search("test")
