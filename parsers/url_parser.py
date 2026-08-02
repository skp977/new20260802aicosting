"""
============================================================
FILE NAME
url_parser.py

PURPOSE
Fetch and extract readable text from a website URL.

INPUT
URL string

OUTPUT
{"text": ..., "source": ..., "type": "url"}

DEPENDENCIES
trafilatura (primary), requests + BeautifulSoup (fallback)

LAST UPDATED
2026-08-02
============================================================
"""

import requests


class URLParser:

    def parse(self, source):

        try:
            text = self._trafilatura(source)
            engine = "trafilatura"
        except Exception:
            try:
                text = self._beautifulsoup(source)
                engine = "beautifulsoup"
            except Exception:
                text = ""
                engine = "unavailable"

        return {
            "text": text,
            "source": str(source),
            "type": "url",
            "engine": engine
        }

    def _trafilatura(self, url):
        import trafilatura

        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return ""

        return trafilatura.extract(downloaded) or ""

    def _beautifulsoup(self, url):
        from bs4 import BeautifulSoup

        response = requests.get(
            url,
            timeout=30,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        return soup.get_text("\n", strip=True)
