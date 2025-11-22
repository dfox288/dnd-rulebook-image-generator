import requests
from typing import Dict, Any, Iterator, Optional
import logging

logger = logging.getLogger(__name__)


class DndApiClient:
    """Client for fetching data from D&D Compendium API"""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def fetch_entities(
        self,
        entity_type: str,
        limit: Optional[int] = None,
        per_page: int = 100
    ) -> Iterator[Dict[str, Any]]:
        """
        Fetch entities from API with pagination support

        Args:
            entity_type: Type of entity (spells, items, etc.)
            limit: Maximum number of entities to fetch (None = all)
            per_page: Number of entities per page

        Yields:
            Entity dictionaries
        """
        page = 1
        fetched = 0

        while True:
            # Stop if we've reached the limit
            if limit and fetched >= limit:
                break

            # Fetch page
            url = f"{self.base_url}/{entity_type}"
            params = {"page": page, "per_page": per_page}

            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as e:
                logger.error(f"Failed to fetch {entity_type} page {page}: {e}")
                break

            # Yield entities
            entities = data.get("data", [])
            for entity in entities:
                if limit and fetched >= limit:
                    break
                yield entity
                fetched += 1

            # Check if we've reached the last page
            meta = data.get("meta", {})
            current_page = meta.get("current_page", page)
            last_page = meta.get("last_page", page)

            if current_page >= last_page:
                break

            page += 1
