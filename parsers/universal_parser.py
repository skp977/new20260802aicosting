"""
============================================================
FILE NAME
universal_parser.py

PURPOSE
Master parser controller - detect input type and dispatch
to the right parser.

INPUT
Anything (file path, URL, raw text)

OUTPUT
{"text": ..., "source": ..., "type": ...}

USED BY
main.py (/generate)
FastAPI api/main_api.py

LAST UPDATED
2026-08-02
============================================================
"""

from pathlib import Path

from parsers.document_parser import DocumentParser
from parsers.image_parser import ImageParser
from parsers.email_parser import EmailParser
from parsers.url_parser import URLParser
from parsers.voice_parser import VoiceParser
from parsers.table_parser import TableParser


class UniversalParser:

    def __init__(self):

        self.document_parser = DocumentParser()

        self.image_parser = ImageParser()

        self.email_parser = EmailParser()

        self.url_parser = URLParser()

        self.voice_parser = VoiceParser()

        self.table_parser = TableParser()

    def parse(self, source):

        source = str(source)

        if source.startswith("http://") or source.startswith("https://"):
            return self.url_parser.parse(source)

        if source.lower().startswith(("from:", "to:", "subject:")):
            return self.email_parser.parse(source)

        if "@" in source and "\n" in source and not Path(source).is_file():
            return self.email_parser.parse(source)

        path = Path(source)

        if path.is_file():
            return self.parse_file(path)

        return {
            "text": source,
            "source": source,
            "type": "raw_text"
        }

    def parse_file(self, path):

        path = Path(path)

        ext = path.suffix.lower()

        if ext in [".pdf", ".docx", ".txt", ".rtf"]:
            return self.document_parser.parse(path)

        if ext in [".xlsx", ".xls", ".csv"]:
            return self.table_parser.parse(path)

        if ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"]:
            return self.image_parser.parse(path)

        if ext in [".wav", ".mp3", ".m4a", ".ogg"]:
            return self.voice_parser.parse(path)

        if ext in [".eml"]:
            return self.email_parser.parse(path)

        return {
            "text": str(path),
            "source": str(path),
            "type": "unknown"
        }
