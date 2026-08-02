"""
FILE NAME:
search_engine.py

PURPOSE:
Perform live web searches (DuckDuckGo, keyless) to gather current
itinerary and pricing data from the internet for AI itinerary
generation. Gracefully returns [] if search is unavailable.

OUTPUT:
List of result dicts: [{"title", "url", "snippet"}, ...]

USED BY:
itinerary/ai_itinerary_generator.py

LAST UPDATED:
2026-08-02
"""

import logging
import os

logger = logging.getLogger(__name__)


class WebSearchEngine:

    def __init__(self, provider="duckduckgo", max_results=None, timeout=None):

        self.provider = provider or os.getenv("SEARCH_PROVIDER", "duckduckgo")
        self.max_results = int(
            max_results or os.getenv("SEARCH_MAX_RESULTS", "5")
        )
        self.timeout = int(
            timeout or os.getenv("SEARCH_TIMEOUT", "20")
        )

    def enabled(self):

        return os.getenv(
            "WEB_SEARCH_ENABLED", "true"
        ).strip().lower() in {"1", "true", "yes", "on"}

    def search(self, query, max_results=None):

        if not self.enabled():
            logger.info("Web search disabled (WEB_SEARCH_ENABLED=false)")
            return []

        limit = max_results or self.max_results

        if self.provider == "duckduckgo":
            return self._search_duckduckgo(query, limit)

        logger.warning("Unsupported search provider: %s", self.provider)
        return []

    def _search_duckduckgo(self, query, limit):

        try:
            from ddgs import DDGS

            with DDGS(timeout=self.timeout) as ddg:
                results = list(
                    ddg.text(query, max_results=limit)
                )

            cleaned = []

            for item in results:
                title = (item.get("title") or "").strip()
                url = (item.get("href") or "").strip()
                body = (item.get("body") or "").strip()

                if not title and not body:
                    continue

                cleaned.append(
                    {
                        "title": title,
                        "url": url,
                        "snippet": body,
                    }
                )

            logger.info(
                "Web search returned %d result(s) for query: %s",
                len(cleaned),
                query[:80],
            )

            return cleaned

        except Exception as exc:
            logger.warning(
                "Web search failed for query %r: %s", query, exc
            )
            return []


if __name__ == "__main__":

    engine = WebSearchEngine()

    for result in engine.search(
        "Kathmandu Pokhara Nepal tour package price per person"
    ):
        print(result["title"])
        print("  ", result["url"])
        print("  ", result["snippet"][:140])
