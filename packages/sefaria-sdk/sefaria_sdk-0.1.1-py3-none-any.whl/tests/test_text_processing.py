"""
Tests for the TextProcessor class.
"""

import pytest

from sefaria_sdk.text_processing import TextProcessor


class TestTextProcessor:
    """Test cases for TextProcessor utilities."""

    def test_extract_verses_from_list(self):
        """Test extracting verses from list format."""
        text_data = {
            "text": ["In the beginning", "God created", "the heavens and earth"]
        }

        verses = TextProcessor.extract_verses(text_data)

        assert len(verses) == 3
        assert verses[0] == "In the beginning"
        assert verses[1] == "God created"
        assert verses[2] == "the heavens and earth"

    def test_extract_verses_from_string(self):
        """Test extracting verses from string format."""
        text_data = {"text": "In the beginning\nGod created\nthe heavens and earth"}

        verses = TextProcessor.extract_verses(text_data)

        assert len(verses) == 3
        assert verses[0] == "In the beginning"
        assert verses[1] == "God created"
        assert verses[2] == "the heavens and earth"

    def test_extract_verses_from_hebrew(self):
        """Test extracting verses from Hebrew text field."""
        text_data = {"he": ["בְּרֵאשִׁית", "בָּרָא אֱלֹהִים", "אֵת הַשָּׁמַיִם"]}

        verses = TextProcessor.extract_verses(text_data)

        assert len(verses) == 3
        assert "בְּרֵאשִׁית" in verses[0]

    def test_extract_verses_from_versions(self):
        """Test extracting verses from versions array."""
        text_data = {"versions": [{"text": ["First verse", "Second verse"]}]}

        verses = TextProcessor.extract_verses(text_data)

        assert len(verses) == 2
        assert verses[0] == "First verse"
        assert verses[1] == "Second verse"

    def test_extract_verses_empty_input(self):
        """Test extracting verses from empty input."""
        assert TextProcessor.extract_verses({}) == []
        assert TextProcessor.extract_verses(None) == []
        assert TextProcessor.extract_verses("not a dict") == []

    def test_extract_verses_filters_empty(self):
        """Test that empty verses are filtered out."""
        text_data = {"text": ["Valid verse", "", "  ", "Another verse", None]}

        verses = TextProcessor.extract_verses(text_data)

        assert len(verses) == 2
        assert verses[0] == "Valid verse"
        assert verses[1] == "Another verse"

    def test_format_hebrew_basic(self):
        """Test basic Hebrew formatting."""
        hebrew = "בְּרֵאשִׁית"
        formatted = TextProcessor.format_hebrew(hebrew)

        assert formatted.startswith("\u200f")  # RTL marker
        assert hebrew in formatted

    def test_format_hebrew_empty(self):
        """Test Hebrew formatting with empty input."""
        assert TextProcessor.format_hebrew("") == ""
        assert TextProcessor.format_hebrew(None) == ""

    def test_format_hebrew_already_has_rtl(self):
        """Test Hebrew formatting when RTL marker already present."""
        hebrew = "\u200fבְּרֵאשִׁית"
        formatted = TextProcessor.format_hebrew(hebrew)

        # Should not add another RTL marker
        assert formatted.count("\u200f") == 1

    def test_format_hebrew_strips_whitespace(self):
        """Test that Hebrew formatting strips whitespace."""
        hebrew = "  בְּרֵאשִׁית  "
        formatted = TextProcessor.format_hebrew(hebrew)

        assert not formatted.endswith(" ")
        assert formatted.strip() == formatted

    def test_get_parallel_texts_lists(self):
        """Test parallel text alignment with lists."""
        hebrew = ["בְּרֵאשִׁית", "בָּרָא אֱלֹהִים"]
        english = ["In the beginning", "God created"]

        pairs = TextProcessor.get_parallel_texts(hebrew, english)

        assert len(pairs) == 2
        assert hebrew[0] in pairs[0][0]
        assert pairs[0][1] == "In the beginning"
        assert hebrew[1] in pairs[1][0]
        assert pairs[1][1] == "God created"

    def test_get_parallel_texts_strings(self):
        """Test parallel text alignment with strings."""
        hebrew = "בְּרֵאשִׁית"
        english = "In the beginning"

        pairs = TextProcessor.get_parallel_texts(hebrew, english)

        assert len(pairs) == 1
        assert hebrew in pairs[0][0]
        assert pairs[0][1] == "In the beginning"

    def test_get_parallel_texts_mismatched_lengths(self):
        """Test parallel text alignment with mismatched lengths."""
        hebrew = ["בְּרֵאשִׁית", "בָּרָא אֱלֹהִים", "אֵת הַשָּׁמַיִם"]
        english = ["In the beginning", "God created"]

        pairs = TextProcessor.get_parallel_texts(hebrew, english)

        assert len(pairs) == 3
        assert pairs[2][1] == ""  # Empty English for third Hebrew verse

    def test_get_parallel_texts_more_english(self):
        """Test parallel text alignment with more English verses."""
        hebrew = ["בְּרֵאשִׁית"]
        english = ["In the beginning", "God created", "the heavens"]

        pairs = TextProcessor.get_parallel_texts(hebrew, english)

        assert len(pairs) == 3
        assert pairs[1][0] == ""  # Empty Hebrew for second English verse
        assert pairs[2][0] == ""  # Empty Hebrew for third English verse

    def test_get_parallel_texts_filters_empty(self):
        """Test that parallel texts filter out empty verses."""
        hebrew = ["בְּרֵאשִׁית", "", "בָּרָא אֱלֹהִים"]
        english = ["In the beginning", "God created"]

        pairs = TextProcessor.get_parallel_texts(hebrew, english)

        # Should have 2 Hebrew verses (empty one filtered) and 2 English
        assert len(pairs) == 2

    def test_clean_text_basic(self):
        """Test basic text cleaning."""
        text = "This   is  a   test."
        cleaned = TextProcessor.clean_text(text)

        assert cleaned == "This is a test."

    def test_clean_text_punctuation(self):
        """Test text cleaning with punctuation spacing."""
        text = "Hello , world ! How are you ?"
        cleaned = TextProcessor.clean_text(text)

        assert cleaned == "Hello, world! How are you?"

    def test_clean_text_multiple_punctuation(self):
        """Test text cleaning with multiple punctuation marks."""
        text = "Test  ;  another : test ."
        cleaned = TextProcessor.clean_text(text)

        assert cleaned == "Test; another: test."

    def test_clean_text_strips_whitespace(self):
        """Test that text cleaning strips leading/trailing whitespace."""
        text = "  Hello world  "
        cleaned = TextProcessor.clean_text(text)

        assert cleaned == "Hello world"

    def test_clean_text_empty(self):
        """Test text cleaning with empty input."""
        assert TextProcessor.clean_text("") == ""
        assert TextProcessor.clean_text(None) == ""
        assert TextProcessor.clean_text("   ") == ""

    def test_clean_text_newlines_and_tabs(self):
        """Test text cleaning with newlines and tabs."""
        text = "Hello\t\tworld\n\ntest"
        cleaned = TextProcessor.clean_text(text)

        assert cleaned == "Hello world test"

    def test_extract_verses_mixed_types(self):
        """Test extracting verses with mixed data types."""
        text_data = {"text": ["String verse", 123, None, "Another string", ""]}

        verses = TextProcessor.extract_verses(text_data)

        assert len(verses) == 3  # String, number converted to string, another string
        assert verses[0] == "String verse"
        assert verses[1] == "123"
        assert verses[2] == "Another string"

    def test_format_hebrew_with_numbers(self):
        """Test Hebrew formatting with numbers and mixed content."""
        hebrew = "פרק א׳"
        formatted = TextProcessor.format_hebrew(hebrew)

        assert formatted.startswith("\u200f")
        assert "פרק א׳" in formatted

    def test_get_parallel_texts_empty_inputs(self):
        """Test parallel texts with empty inputs."""
        pairs = TextProcessor.get_parallel_texts([], [])
        assert pairs == []

        pairs = TextProcessor.get_parallel_texts(["test"], [])
        assert len(pairs) == 1
        assert pairs[0][1] == ""

        pairs = TextProcessor.get_parallel_texts([], ["test"])
        assert len(pairs) == 1
        assert pairs[0][0] == ""
