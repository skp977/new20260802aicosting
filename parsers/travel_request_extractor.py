"""
FILE NAME: travel_request_extractor.py

PURPOSE:
Convert any inquiry into a standardized TravelRequest object.

SUPPORTED INPUT:
- Email body
- PDF extracted text
- DOCX extracted text
- OCR text
- Website content
- WhatsApp messages
- Raw text
- AI generated content

OUTPUT:
- TravelRequest object

USED BY:
- orchestrators/manual_request_orchestrator.py
- orchestrators/email_request_orchestrator.py

DEPENDENCIES:
- models.travel_request
- translators.language_engine

EXTRACTS:
- Email
- Phone
- Customer Name
- Pax
- Budget
- Currency
- Destinations
- Hotels
- Activities
- Arrival Date
- Departure Date

LAST UPDATED:
- 2026-06-04
"""

import re

from models.travel_request import TravelRequest
from translators.language_engine import translate_to_english


class TravelRequestExtractor:

    def extract(self, raw_text):

        english_text, language = translate_to_english(raw_text)

        request = TravelRequest()

        request.raw_text = raw_text
        request.translated_text = english_text

        request.original_language = language
        request.language = "en"

        self.extract_email(request, english_text)
        self.extract_phone(request, english_text)
        self.extract_name(request, english_text)

        self.extract_pax(request, english_text)
        self.extract_duration(request, english_text)
        self.extract_budget(request, english_text)

        self.extract_destinations(request, english_text)
        self.extract_dates(request, english_text)
        self.extract_hotels(request, english_text)
        self.extract_activities(request, english_text)

        return request

    # --------------------------------------------------
    # NAME
    # --------------------------------------------------

    def extract_name(self, request, text):

        patterns = [
            r"my name is\s+([A-Za-z ]+)",
            r"i am\s+([A-Za-z ]+)",
            r"this is\s+([A-Za-z ]+)"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                request.customer_name = (
                    match.group(1)
                    .strip()
                    .title()
                )

                return

    # --------------------------------------------------
    # EMAIL
    # --------------------------------------------------

    def extract_email(self, request, text):

        match = re.search(
            r'[\w\.-]+@[\w\.-]+\.\w+',
            text
        )

        if match:
            request.customer_email = match.group()

    # --------------------------------------------------
    # PHONE
    # --------------------------------------------------

    def extract_phone(self, request, text):

        match = re.search(
            r'(\+?\d[\d\s\-]{7,20})',
            text
        )

        if match:
            request.customer_phone = match.group().strip()

    # --------------------------------------------------
    # PAX
    # --------------------------------------------------

    def extract_pax(self, request, text):

        patterns = [
            r'(\d+)\s+pax',
            r'group\s+of\s+(\d+)',
            r'(\d+)\s+people',
            r'(\d+)\s+persons',
            r'(\d+)\s+travelers',
            r'(\d+)\s+travellers',
            r'(\d+)\s+guests',
            r'family\s+of\s+(\d+)'
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text.lower()
            )

            if match:

                request.pax = int(
                    match.group(1)
                )

                return

        if re.search(
            r'\bcouple\b|honeymoon',
            text.lower()
        ):

            request.pax = 2

            return

        adult = re.search(
            r'(\d+)\s+adult',
            text.lower()
        )

        child = re.search(
            r'(\d+)\s+(?:kid|child|children)',
            text.lower()
        )

        if adult:

            request.pax = int(adult.group(1))

            if child:

                request.pax += int(child.group(1))

        elif child:

            request.pax = int(child.group(1))

    # --------------------------------------------------
    # DURATION
    # --------------------------------------------------

    def extract_duration(self, request, text):

        lower = text.lower()

        day_match = re.search(
            r'(\d+)\s*(?:days|day|d)\b',
            lower
        )

        night_match = re.search(
            r'(\d+)\s*(?:nights|night|n)\b',
            lower
        )

        if day_match:
            request.days = int(day_match.group(1))

        if night_match:
            request.nights = int(night_match.group(1))

        if request.days <= 0 and request.nights > 0:
            request.days = request.nights + 1

        if request.nights <= 0 and request.days > 0:
            request.nights = request.days - 1


    # --------------------------------------------------
    # BUDGET
    # --------------------------------------------------

    def extract_budget(self, request, text):

        match = re.search(
            r'(\d+(?:\.\d+)?)\s*(usd|dollar|npr|eur|gbp)',
            text.lower()
        )

        if match:

            request.budget = float(
                match.group(1)
            )

            request.currency = (
                match.group(2)
            ).upper()

    # --------------------------------------------------
    # DESTINATIONS
    # --------------------------------------------------

    def extract_destinations(
        self,
        request,
        text
    ):

        destinations = []

        nepal_places = [
            "kathmandu",
            "pokhara",
            "chitwan",
            "lumbini",
            "nagarkot",
            "muktinath",
            "janakpur",
            "mustang",
            "everest",
            "annapurna",
            "bandipur",
            "ghandruk",
            "dhulikhel"
        ]

        lower = text.lower()

        for place in nepal_places:

            if place in lower:

                destinations.append(
                    place.title()
                )

        request.destinations = destinations

    # --------------------------------------------------
    # DATES
    # --------------------------------------------------

    def extract_dates(
        self,
        request,
        text
    ):

        patterns = [
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}/\d{1,2}/\d{4})'
        ]

        dates = []

        for pattern in patterns:

            dates.extend(
                re.findall(
                    pattern,
                    text
                )
            )

        if len(dates) >= 1:
            request.arrival_date = dates[0]

        if len(dates) >= 2:
            request.departure_date = dates[1]

    # --------------------------------------------------
    # HOTELS
    # --------------------------------------------------

    def extract_hotels(
        self,
        request,
        text
    ):

        hotels = []

        known_hotels = [
            "yak and yeti",
            "marriott",
            "hilton",
            "hyatt",
            "fish tail lodge",
            "barahi",
            "temple tree",
            "soaltee"
        ]

        lower = text.lower()

        for hotel in known_hotels:

            if hotel in lower:

                hotels.append(
                    hotel.title()
                )

        request.hotels = hotels

    # --------------------------------------------------
    # ACTIVITIES
    # --------------------------------------------------

    def extract_activities(
        self,
        request,
        text
    ):

        activities = []

        keywords = [
            "everest flight",
            "paragliding",
            "rafting",
            "safari",
            "bungee",
            "helicopter",
            "trekking",
            "hiking",
            "boating",
            "city tour"
        ]

        lower = text.lower()

        for item in keywords:

            if item in lower:
                activities.append(item)

        request.activities = activities