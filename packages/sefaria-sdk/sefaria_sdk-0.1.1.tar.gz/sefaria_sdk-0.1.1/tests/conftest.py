"""
Pytest configuration and shared fixtures.
"""

from unittest.mock import Mock

import pytest

from sefaria_sdk.client import SefariaClient


@pytest.fixture
def sefaria_client():
    """Fixture providing a SefariaClient instance."""
    return SefariaClient()


@pytest.fixture
def mock_text_response():
    """Fixture providing a mock text API response."""
    return {
        "ref": "Genesis 1:1",
        "versions": [
            {
                "text": ["In the beginning God created the heaven and the earth."],
                "language": "en",
                "versionTitle": "JPS 1917",
            }
        ],
        "he": ["בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ"],
    }


@pytest.fixture
def mock_search_response():
    """Fixture providing a mock search API response."""
    return {
        "hits": {
            "total": 3,
            "hits": [
                {"_source": {"ref": "Genesis 1:1", "content": "In the beginning"}},
                {
                    "_source": {
                        "ref": "Psalms 23:1",
                        "content": "The Lord is my shepherd",
                    }
                },
                {
                    "_source": {
                        "ref": "Ecclesiastes 3:1",
                        "content": "To every thing there is a season",
                    }
                },
            ],
        }
    }


@pytest.fixture
def mock_related_response():
    """Fixture providing a mock related content API response."""
    return {
        "links": [
            {"ref": "Rashi on Genesis 1:1", "type": "commentary"},
            {"ref": "Ibn Ezra on Genesis 1:1", "type": "commentary"},
            {"ref": "Ramban on Genesis 1:1", "type": "commentary"},
        ]
    }


@pytest.fixture
def mock_languages_response():
    """Fixture providing a mock languages API response."""
    return {
        "en": ["JPS 1917", "Robert Alter", "Sefaria Community Translation"],
        "he": ["Tanach with Text Only", "Miqra according to the Masorah"],
        "es": ["Traducción Española"],
    }


@pytest.fixture
def sample_hebrew_text():
    """Fixture providing sample Hebrew text for testing."""
    return [
        "בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ",
        "וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם",
        "וַיֹּאמֶר אֱלֹהִים יְהִי אוֹר וַיְהִי־אוֹר",
    ]


@pytest.fixture
def sample_english_text():
    """Fixture providing sample English text for testing."""
    return [
        "In the beginning God created the heaven and the earth.",
        "And the earth was without form, and void; and darkness was upon the face of the deep.",
        "And God said, Let there be light: and there was light.",
    ]
