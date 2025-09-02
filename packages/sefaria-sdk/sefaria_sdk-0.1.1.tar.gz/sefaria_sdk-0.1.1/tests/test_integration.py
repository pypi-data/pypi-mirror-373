"""
Integration tests for the Sefaria SDK.
These tests use mock responses to simulate real API interactions.
"""

import json
from unittest.mock import Mock, patch

import pytest

from sefaria_sdk.client import SefariaClient
from sefaria_sdk.text_processing import TextProcessor


class TestIntegration:
    """Integration tests combining client and text processing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = SefariaClient()

    @patch("requests.Session.get")
    def test_full_text_retrieval_and_processing(self, mock_get):
        """Test complete workflow: retrieve text and process it."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "ref": "Genesis 1:1-3",
            "versions": [
                {
                    "text": [
                        "In the beginning God created the heaven and the earth.",
                        "And the earth was without form, and void; and darkness was upon the face of the deep.",
                        "And God said, Let there be light: and there was light.",
                    ]
                }
            ],
            "he": [
                "בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ",
                "וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם",
                "וַיֹּאמֶר אֱלֹהִים יְהִי אוֹר וַיְהִי־אוֹר",
            ],
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Retrieve text
        text_data = self.client.get_text("Genesis 1:1-3")

        # Process English verses from versions array
        english_verses = TextProcessor.extract_verses(
            {"text": text_data["versions"][0]["text"]}
        )
        assert len(english_verses) == 3
        assert "In the beginning" in english_verses[0]

        # Process Hebrew verses
        hebrew_verses = TextProcessor.extract_verses({"text": text_data["he"]})
        assert len(hebrew_verses) == 3

        # Create parallel texts
        parallel = TextProcessor.get_parallel_texts(text_data["he"], english_verses)
        assert len(parallel) == 3
        assert "בְּרֵאשִׁית" in parallel[0][0]
        assert "In the beginning" in parallel[0][1]

    @patch("requests.Session.post")
    def test_search_and_text_retrieval_workflow(self, mock_post):
        """Test workflow: search for texts, then retrieve specific results."""
        # Mock search response
        mock_response = Mock()
        mock_response.json.return_value = {
            "hits": {
                "total": 2,
                "hits": [
                    {"_source": {"ref": "Genesis 1:1"}},
                    {"_source": {"ref": "Psalms 23:1"}},
                ],
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Search for texts
        search_results = self.client.search("beginning")

        # Verify search results
        assert search_results["hits"]["total"] == 2
        refs = [hit["_source"]["ref"] for hit in search_results["hits"]["hits"]]
        assert "Genesis 1:1" in refs
        assert "Psalms 23:1" in refs

    @patch("requests.Session.get")
    def test_text_cleaning_integration(self, mock_get):
        """Test text retrieval with cleaning and processing."""
        # Mock response with messy text
        mock_response = Mock()
        mock_response.json.return_value = {
            "versions": [
                {
                    "text": [
                        "  In the beginning   God created  ",
                        "the heaven  and   the earth . ",
                    ]
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Retrieve and process
        text_data = self.client.get_text("Genesis 1:1-2")
        verses = TextProcessor.extract_verses(text_data)

        # Clean the verses
        cleaned_verses = [TextProcessor.clean_text(verse) for verse in verses]

        assert cleaned_verses[0] == "In the beginning God created"
        assert cleaned_verses[1] == "the heaven and the earth."

    @patch("requests.Session.get")
    def test_error_handling_integration(self, mock_get):
        """Test error handling in integrated workflow."""
        # Mock HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_get.return_value = mock_response

        # Should raise exception
        with pytest.raises(Exception):
            self.client.get_text("Invalid Reference")

    @patch("requests.Session.get")
    def test_multilingual_text_processing(self, mock_get):
        """Test processing texts in multiple languages."""
        # Mock response with multiple language versions
        mock_response = Mock()
        mock_response.json.return_value = {
            "ref": "Genesis 1:1",
            "versions": [
                {
                    "language": "en",
                    "text": ["In the beginning God created the heaven and the earth."],
                },
                {"language": "he", "text": ["בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ"]},
            ],
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        text_data = self.client.get_text("Genesis 1:1")

        # Extract from different version structures
        english_text = text_data["versions"][0]["text"]
        hebrew_text = text_data["versions"][1]["text"]

        # Process both languages
        english_verses = TextProcessor.extract_verses({"text": english_text})
        hebrew_verses = TextProcessor.extract_verses({"text": hebrew_text})

        assert len(english_verses) == 1
        assert len(hebrew_verses) == 1
        assert "In the beginning" in english_verses[0]
        assert "בְּרֵאשִׁית" in hebrew_verses[0]

    @patch("requests.Session.get")
    def test_related_content_workflow(self, mock_get):
        """Test retrieving and processing related content."""
        # Mock related content response
        mock_response = Mock()
        mock_response.json.return_value = {
            "links": [
                {"ref": "Rashi on Genesis 1:1", "type": "commentary"},
                {"ref": "Ibn Ezra on Genesis 1:1", "type": "commentary"},
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        related = self.client.get_related("Genesis 1:1")

        assert len(related["links"]) == 2
        refs = [link["ref"] for link in related["links"]]
        assert "Rashi on Genesis 1:1" in refs
        assert "Ibn Ezra on Genesis 1:1" in refs

    def test_text_processor_edge_cases(self):
        """Test text processor with various edge cases."""
        # Test with None values
        assert TextProcessor.extract_verses(None) == []
        assert TextProcessor.clean_text(None) == ""
        assert TextProcessor.format_hebrew(None) == ""

        # Test with empty structures
        assert TextProcessor.extract_verses({"text": []}) == []
        assert TextProcessor.get_parallel_texts([], []) == []

        # Test with mixed content
        mixed_data = {"text": ["Valid text", None, "", "  ", "Another valid"]}
        verses = TextProcessor.extract_verses(mixed_data)
        assert len(verses) == 2
        assert verses[0] == "Valid text"
        assert verses[1] == "Another valid"
