"""
FILE NAME: language_engine.py
PURPOSE: Detect and translate customer language
INPUT: Any language text
OUTPUT: English text + detected language
USED BY: Email, Parser, Itinerary
DEPENDENCIES: langdetect, deep_translator
LAST UPDATED: 2026-06-04
"""

from langdetect import detect
from deep_translator import GoogleTranslator


def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"


def translate_to_english(text):
    try:
        lang = detect_language(text)

        if lang == "en":
            return text, lang

        translated = GoogleTranslator(
            source="auto",
            target="en"
        ).translate(text)

        return translated, lang

    except Exception:
        return text, "en"


def translate_from_english(text, target_language):
    try:

        if target_language == "en":
            return text

        return GoogleTranslator(
            source="en",
            target=target_language
        ).translate(text)

    except:
        return text