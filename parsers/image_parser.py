"""
============================================================
FILE NAME
image_parser.py

PURPOSE
Parse images via OCR.

INPUT
Image file path (jpg, jpeg, png, webp, bmp, tiff)

OUTPUT
{"text": ..., "source": ..., "type": "image"}

USED BY
UniversalParser

LAST UPDATED
2026-08-02
============================================================
"""

from parsers.ocr_parser import OCRParser


class ImageParser:

    def __init__(self):
        self.ocr = OCRParser()

    def parse(self, source):

        result = self.ocr.parse(source)

        result["type"] = "image"

        return result
