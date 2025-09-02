"""
Text processing utilities for Sefaria texts.

This module provides utilities for handling Hebrew and English texts from Sefaria,
including verse extraction, Hebrew text formatting, and parallel text alignment.
"""

import re
from typing import Dict, List, Optional, Tuple, Union


class TextProcessor:
    """Utilities for processing and formatting Sefaria texts."""

    @staticmethod
    def extract_verses(text_data: Dict) -> List[str]:
        """Extract individual verses from text response.

        Args:
            text_data: Dictionary containing Sefaria API response

        Returns:
            List of verses extracted from the response

        Example:
            >>> response = client.get_text("Genesis 1")
            >>> verses = TextProcessor.extract_verses(response)
            >>> print(verses[0])  # First verse
        """
        if not isinstance(text_data, dict):
            return []

        # Try different possible locations for text content
        text = None

        # Check for text in response
        if "text" in text_data:
            text = text_data["text"]
        # Check for Hebrew text
        elif "he" in text_data:
            text = text_data["he"]
        # Check in versions array
        elif "versions" in text_data and text_data["versions"]:
            text = text_data["versions"][0].get("text", [])

        # Handle different text formats
        if isinstance(text, list):
            return [
                str(verse).strip() for verse in text if verse and str(verse).strip()
            ]
        elif isinstance(text, str):
            verses = re.split(r"[\n\r]+", text)
            return [verse.strip() for verse in verses if verse and verse.strip()]

        return []

    @staticmethod
    def format_hebrew(text: str) -> str:
        """Format Hebrew text with proper RTL and nikud handling.

        Args:
            text: Hebrew text string to format

        Returns:
            Formatted Hebrew text with proper RTL markers and nikud

        Example:
            >>> hebrew = "בְּרֵאשִׁית"
            >>> formatted = TextProcessor.format_hebrew(hebrew)
        """
        if not text:
            return ""

        # Add RTL marker if not present
        if not text.startswith("\u200f"):
            text = "\u200f" + text

        # Note: Hebrew text formatting - keeping original text intact
        # The nikud normalization was causing issues with character order

        # Add final formatting
        text = text.strip()

        return text

    @staticmethod
    def get_parallel_texts(
        hebrew: Union[str, List[str]], english: Union[str, List[str]]
    ) -> List[Tuple[str, str]]:
        """Align Hebrew and English texts verse by verse.

        Args:
            hebrew: Hebrew text (string or list of verses)
            english: English text (string or list of verses)

        Returns:
            List of (hebrew, english) verse pairs

        Example:
            >>> he_text = client.get_text("Genesis 1")['he']
            >>> en_text = client.get_text("Genesis 1", version="english")['text']
            >>> pairs = TextProcessor.get_parallel_texts(he_text, en_text)
            >>> for he, en in pairs:
            ...     print(f"{he} | {en}")
        """
        # Convert inputs to lists if they're strings
        if isinstance(hebrew, str):
            hebrew = [hebrew]
        if isinstance(english, str):
            english = [english]

        # Format Hebrew verses
        hebrew = [TextProcessor.format_hebrew(str(verse)) for verse in hebrew if verse]
        english = [str(verse).strip() for verse in english if verse]

        # Pair verses, handling mismatched lengths
        max_verses = max(len(hebrew), len(english))
        pairs = []

        for i in range(max_verses):
            he_verse = hebrew[i] if i < len(hebrew) else ""
            en_verse = english[i] if i < len(english) else ""
            pairs.append((he_verse, en_verse))

        return pairs

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text by removing extra spaces and normalizing punctuation.

        Args:
            text: Text string to clean

        Returns:
            Cleaned and normalized text

        Example:
            >>> text = "This   is  a  text ."
            >>> clean = TextProcessor.clean_text(text)
            >>> print(clean)  # "This is a text."
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Normalize punctuation spacing
        text = re.sub(r"\s*([.,;:!?])", r"\1", text)

        # Remove spaces at start/end
        text = text.strip()

        return text
