from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class SefariaClient:
    """Client for interacting with the Sefaria API."""

    def __init__(
        self,
        base_url: str = "https://www.sefaria.org/api",
        user_agent: Optional[str] = None,
    ):
        """Initialize the Sefaria client.

        Args:
            base_url: Base URL for the Sefaria API. Defaults to https://www.sefaria.org/api
            user_agent: Optional custom user agent string
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

        # Configure retries
        retries = Retry(
            total=4,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.session.mount("http://", HTTPAdapter(max_retries=retries))

        # Set default headers
        self.headers = {
            "Accept": "application/json",
            "User-Agent": user_agent or "Unofficial-Sefaria-Python-SDK/0.1",
        }

    def get_text(self, tref: str, **kwargs) -> Dict:
        """Get a text from Sefaria using the v3 texts API.

        Args:
            tref: A Sefaria-specific reference
            **kwargs: Additional parameters passed to the API (language, direction, context, etc.)

        Returns:
            Dict containing the requested text and metadata
        """
        endpoint = f"{self.base_url}/v3/texts/{quote(tref)}"
        response = self.session.get(
            endpoint, params=kwargs, headers=self.headers, timeout=15
        )
        response.raise_for_status()
        return response.json()

    def get_versions(self, index: str) -> List[Dict]:
        """Get all available versions of a text.

        Args:
            index: A valid Sefaria index title

        Returns:
            List of dictionaries containing version metadata
        """
        endpoint = f"{self.base_url}/texts/versions/{quote(index)}"
        response = self.session.get(endpoint, headers=self.headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_manuscripts(self, tref: str) -> Dict:
        """Get manuscript data for a text reference.

        Args:
            tref: A valid Sefaria text reference

        Returns:
            Dict containing manuscript data and metadata
        """
        endpoint = f"{self.base_url}/manuscripts/{quote(tref)}"
        response = self.session.get(endpoint, headers=self.headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_random_text(
        self, titles: Optional[str] = None, categories: Optional[str] = None
    ) -> Dict:
        """Get a random text reference.

        Args:
            titles: Optional pipe-separated string of book titles
            categories: Optional pipe-separated string of categories

        Returns:
            Dict containing random text reference
        """
        endpoint = f"{self.base_url}/texts/random"
        params = {}

        if titles:
            params["titles"] = titles
        if categories:
            params["categories"] = categories

        response = requests.get(endpoint, params=params, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_index(self, index_title: str) -> Dict:
        """Get the full index record for a text.

        Args:
            index_title: Title of a valid Sefaria index

        Returns:
            Dict containing the full index record
        """
        endpoint = f"{self.base_url}/v2/raw/index/{quote(index_title)}"
        response = self.session.get(endpoint, headers=self.headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_table_of_contents(self) -> Dict:
        """Get the complete table of contents.

        Returns:
            Dict containing the complete table of contents
        """
        endpoint = f"{self.base_url}/index"
        response = self.session.get(endpoint, headers=self.headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_ref_topic_links(self, tref: str) -> Dict:
        """Get topic links for a text reference.

        Args:
            tref: A valid Sefaria text reference

        Returns:
            Dict containing topic links
        """
        endpoint = f"{self.base_url}/ref-topic-links/{quote(tref)}"
        response = self.session.get(endpoint, headers=self.headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_translations(self, lang: str) -> Dict:
        """Get translations in a specific language.

        Args:
            lang: ISO 639-1 language code

        Returns:
            Dict containing translations organized by category
        """
        endpoint = f"{self.base_url}/texts/translations/{quote(lang)}"
        response = self.session.get(endpoint, headers=self.headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_languages(self) -> List[str]:
        """Get list of available translation languages.

        Returns:
            List of language codes that have translations
        """
        endpoint = f"{self.base_url}/texts/translations"
        response = self.session.get(endpoint, headers=self.headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def search(
        self,
        query: str,
        type: str = "text",
        field: Optional[str] = None,
        offset: int = 0,
        limit: int = 10,
        **kwargs,
    ) -> Dict:
        """Search Sefaria's library using the search-wrapper endpoint.

        Args:
            query: The search query string (required)
            type: Type of search ("text" or "sheet")
            field: Field to search in (e.g., "exact", "naive_lemmatizer" for text; "content" for sheets)
            offset: Number of results to skip
            limit: Maximum number of results to return
            **kwargs: Additional search parameters (filters, filter_fields, aggs, sort_type, etc.)

        Returns:
            Dict containing search results
        """
        endpoint = f"{self.base_url}/search-wrapper"
        payload = {"query": query, "type": type, "offset": offset, "limit": limit}

        if field:
            payload["field"] = field
        payload.update(kwargs)

        # Map common parameter names
        if "limit" in payload:
            payload["size"] = payload.pop("limit")

        response = self.session.post(
            endpoint, json=payload, headers=self.headers, timeout=20
        )
        response.raise_for_status()
        return response.json()

    def get_counts(self, title: str) -> Dict:
        """Get counts of available texts for a given title.

        Args:
            title: Title to get counts for

        Returns:
            Dict containing text counts
        """
        endpoint = f"{self.base_url}/counts/{quote(title)}"
        response = self.session.get(endpoint, headers=self.headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_text_list(self) -> Dict:
        """Get a list of all available texts.

        Returns:
            Dict containing list of texts
        """
        endpoint = f"{self.base_url}/texts/list"
        response = self.session.get(endpoint, headers=self.headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_links(self, tref: str) -> Dict:
        """Get links for a text reference.

        Args:
            tref: Text reference to get links for

        Returns:
            Dict containing links
        """
        endpoint = f"{self.base_url}/links/{quote(tref)}"
        response = self.session.get(endpoint, headers=self.headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_link_summary(self, tref: str) -> Dict:
        """Get a summary of links for a text reference.

        Args:
            tref: Text reference to get link summary for

        Returns:
            Dict containing link summary
        """
        endpoint = f"{self.base_url}/links/{quote(tref)}/summary"
        response = self.session.get(endpoint, headers=self.headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_related(self, tref: str) -> Dict:
        """Get related content for a text reference using the modern Related API.

        Args:
            tref: Text reference to get related content for

        Returns:
            Dict containing related content (topics, links, etc.)
        """
        endpoint = f"{self.base_url}/related/{quote(tref)}"
        response = self.session.get(endpoint, headers=self.headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_history(
        self, tref: str, language: Optional[str] = None, version: Optional[str] = None
    ) -> Dict:
        """Get history for a text reference.

        Args:
            tref: Text reference to get history for
            language: Optional language filter
            version: Optional version filter

        Returns:
            Dict containing text history
        """
        endpoint = f"{self.base_url}/history/{quote(tref)}"
        params = {}

        if language:
            params["language"] = language
        if version:
            params["version"] = version

        response = requests.get(endpoint, params=params, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_calendar_items(
        self, timezone: Optional[str] = None, custom: Optional[str] = None
    ) -> Dict:
        """Get calendar items.

        Args:
            timezone: Optional timezone
            custom: Optional custom calendar items

        Returns:
            Dict containing calendar items
        """
        endpoint = f"{self.base_url}/calendars"
        params = {}

        if timezone:
            params["timezone"] = timezone
        if custom:
            params["custom"] = custom

        response = self.session.get(
            endpoint, params=params, headers=self.headers, timeout=15
        )
        response.raise_for_status()
        return response.json()

    def get_calendar(self, timezone: Optional[str] = None) -> Dict:
        """Get calendar items (alias for get_calendar_items).

        Args:
            timezone: Optional timezone

        Returns:
            Dict containing calendar items
        """
        return self.get_calendar_items(timezone=timezone)

    def get_ref_data(self, refs: List[str]) -> Dict:
        """Get data for multiple text references.

        Args:
            refs: List of text references

        Returns:
            Dict containing reference data
        """
        endpoint = f"{self.base_url}/bulktext"
        response = self.session.post(
            endpoint, json={"refs": refs}, headers=self.headers, timeout=20
        )
        response.raise_for_status()
        return response.json()
