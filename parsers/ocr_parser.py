"""
============================================================
FILE NAME
ocr_parser.py

PURPOSE
Extract text from images using OCR (Tesseract).

NOTE
Requires the Tesseract engine installed on the system.
Returns a friendly message when it is unavailable.

INPUT
Image file path

OUTPUT
{"text": ..., "source": ..., "type": "ocr"}

DEPENDENCIES
pytesseract, Pillow

LAST UPDATED
2026-08-02
============================================================
"""


import os
import shutil
from pathlib import Path


def _locate_tesseract():
    candidates = [
        os.environ.get("TESSERACT_CMD"),
        shutil.which("tesseract"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        str(Path.home() / "AppData/Local/Programs/Tesseract-OCR/tesseract.exe")
    ]

    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)

    return None


class OCRParser:

    def parse(self, source):
        try:
            import pytesseract
            from PIL import Image

            tesseract_path = _locate_tesseract()

            if not tesseract_path:
                return {
                    "text": (
                        "[OCR unavailable] The Tesseract OCR engine is "
                        "not installed. Install Tesseract (free, open "
                        "source) from https://github.com/UB-Mannheim/"
                        "tesseract and retry."
                    ),
                    "source": str(source),
                    "type": "ocr",
                    "engine": "unavailable"
                }

            pytesseract.pytesseract.tesseract_cmd = tesseract_path

            text = pytesseract.image_to_string(
                Image.open(str(source))
            )

            return {
                "text": text,
                "source": str(source),
                "type": "ocr",
                "engine": "tesseract"
            }
        except Exception:
            return {
                "text": (
                    "[OCR unavailable] Tesseract OCR engine is not "
                    "installed on this machine. Install Tesseract and "
                    "add it to PATH, then retry image parsing."
                ),
                "source": str(source),
                "type": "ocr",
                "engine": "unavailable"
            }
