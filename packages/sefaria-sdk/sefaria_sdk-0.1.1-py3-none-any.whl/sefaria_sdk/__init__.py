"""
Sefaria SDK - A Python interface for the Sefaria API
"""

from .client import SefariaClient
from .text_processing import TextProcessor

__version__ = "0.1.0"
__all__ = ["SefariaClient", "TextProcessor"]
