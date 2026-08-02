"""
FILE NAME:
ai_itinerary_generator.py

PURPOSE:
Generate travel itineraries from a natural-language prompt using the
DeepSeek API (OpenAI-compatible). Falls back to the rule-based
ItineraryEngine when no API key is configured or the AI call fails.

INPUT:
TravelRequest (raw_text / translated_text + extracted fields)

OUTPUT:
Itinerary list in the same schema as ItineraryEngine:
[{day, title, city, overnight, hotel_category, meals, transport,
  activities, notes}, ...]

USED BY:
orchestrators/manual_request_orchestrator.py
orchestrators/email_request_orchestrator.py

LAST UPDATED:
2026-08-02
"""

import json
import logging
import os
import re

from itinerary.itinerary_engine import ItineraryEngine

logger = logging.getLogger(__name__)

HOTEL_CATEGORIES = ["3 Star", "4 Star", "5 Star"]

SYSTEM_PROMPT = (
    "You are a senior Nepal travel itinerary planner with expert local "
    "knowledge. You build realistic, day-by-day itineraries tailored to the "
    "traveler's request.\n\n"
    "Respond with ONLY valid JSON. No markdown, no code fences, no prose.\n"
    'The JSON must be exactly: {"itinerary": [day, day, ...]} where each day '
    'is an object with these keys:\n'
    '  "day": positive integer, sequential starting at 1\n'
    '  "title": short title for the day\n'
    '  "city": real Nepali place (e.g. Kathmandu, Pokhara, Chitwan, '
    "Lumbini, Nagarkot, Bandipur)\n"
    '  "overnight": the place where the traveler sleeps that night\n'
    '  "hotel_category": exactly one of "3 Star", "4 Star", "5 Star"\n'
    '  "meals": array of strings from ["Breakfast", "Lunch", "Dinner"]; '
    "always include Dinner\n"
    '  "transport": one short string, e.g. "Private Vehicle", '
    '"Tourist Bus", "Domestic Flight (KTM-PKR)"\n'
    '  "activities": 3 to 6 concrete real landmarks, tours or experiences '
    "for that day\n"
    '  "notes": one practical sentence (drive time, altitude, packing tip, '
    "etc.)\n\n"
    "Constraints:\n"
    "- Produce the exact number of days requested.\n"
    "- Use real, verifiable places and standard Nepal tourism routes.\n"
    "- Vary the itinerary intelligently; do not repeat the same template."
)


class DeepSeekItineraryGenerator:

    def __init__(self, api_key=None, model=None, base_url=None, timeout=None):

        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.base_url = base_url or os.getenv(
            "DEEPSEEK_BASE_URL", "https://api.deepseek.com"
        )
        self.timeout = int(
            timeout or os.getenv("DEEPSEEK_TIMEOUT", "60")
        )

    def generate(self, request):

        if not self.api_key:
            logger.info("DEEPSEEK_API_KEY not set; AI itinerary skipped")
            return None

        prompt = self._build_prompt(request)

        try:
            content = self._call_api(prompt)
        except Exception as exc:
            logger.warning("DeepSeek itinerary call failed: %s", exc)
            return None

        return self._parse_itinerary(content, request)

    def _build_prompt(self, request):

        lines = []

        raw = (request.raw_text or "").strip()
        if raw:
            lines.append(f"CUSTOMER INQUIRY (verbatim):\n{raw}")

        translated = (request.translated_text or "").strip()
        if translated and translated.lower() != raw.lower():
            lines.append(f"\nTRANSLATED INQUIRY:\n{translated}")

        hints = []
        if request.destinations:
            hints.append("Destinations: " + ", ".join(request.destinations))
        if request.days > 0:
            hints.append(f"Duration: {request.days} days")
        if request.nights > 0:
            hints.append(f"Nights: {request.nights}")
        if request.pax > 0:
            hints.append(
                f"Travelers: {request.pax} pax"
                f" ({request.adults} adults"
                + (f", {request.children} children" if request.children else "")
                + ")"
            )
        if request.arrival_date:
            hints.append(f"Arrival date: {request.arrival_date}")
        if request.departure_date:
            hints.append(f"Departure date: {request.departure_date}")
        if request.budget > 0:
            hints.append(
                f"Budget: {request.currency} {request.budget:g}"
            )
        if request.hotel_category:
            hints.append(f"Hotel preference: {request.hotel_category}")
        if request.travel_style:
            hints.append(f"Travel style: {request.travel_style}")
        if request.meals:
            hints.append("Meals requested: " + ", ".join(request.meals))
        if request.notes:
            hints.append("Notes: " + request.notes)

        if hints:
            lines.append("\nEXTRACTED REQUIREMENTS:\n" + "\n".join(hints))

        if request.days > 0:
            lines.append(
                f"\nIMPORTANT: build exactly {request.days} day(s)."
            )

        return "\n\n".join(lines) or "Build a 3-day Nepal itinerary."

    def _call_api(self, prompt):

        from openai import OpenAI

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=3000,
            response_format={"type": "json_object"},
        )

        return response.choices[0].message.content or ""

    def _parse_itinerary(self, content, request):

        text = content.strip()

        fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
        if fence:
            text = fence.group(1).strip()

        data = json.loads(text)

        if isinstance(data, dict):
            days = data.get("itinerary") or data.get("days") or []
        else:
            days = data

        if not isinstance(days, list) or not days:
            raise ValueError("AI response contained no itinerary days")

        result = []

        for index, day in enumerate(days, start=1):
            if not isinstance(day, dict):
                continue
            result.append(
                self._normalize_day(day, index)
            )

        if not result:
            raise ValueError("AI itinerary was empty after normalization")

        return result

    def _normalize_day(self, day, fallback_day):

        city = str(day.get("city") or day.get("overnight") or "").strip()
        overnight = str(
            day.get("overnight") or day.get("city") or city or "Kathmandu"
        ).strip()

        if not city:
            city = overnight

        activities = day.get("activities") or []
        if isinstance(activities, str):
            activities = [activities]
        activities = [
            str(item).strip()
            for item in activities
            if str(item).strip()
        ]

        meals = day.get("meals") or []
        if isinstance(meals, str):
            meals = [meals]
        meals = [str(item).strip() for item in meals if str(item).strip()]
        if "Dinner" not in meals and "dinner" not in meals:
            meals.append("Dinner")

        hotel_category = self._normalize_hotel_category(
            day.get("hotel_category", "4 Star")
        )

        title = str(day.get("title") or f"Explore {overnight}").strip()

        transport = str(
            day.get("transport") or "Private Vehicle"
        ).strip()

        notes = str(day.get("notes") or "").strip()

        return {
            "day": fallback_day,
            "title": title,
            "city": city,
            "overnight": overnight,
            "hotel_category": hotel_category,
            "meals": meals,
            "transport": transport,
            "activities": activities,
            "notes": notes,
        }

    def _normalize_hotel_category(self, value):

        if value is None:
            return "4 Star"

        text = str(value).lower()

        if "5" in text:
            return "5 Star"
        if "3" in text:
            return "3 Star"

        return "4 Star"


class SmartItineraryGenerator:

    def __init__(self, mode=None):

        self.mode = (mode or os.getenv("ITINERARY_ENGINE", "auto")).lower()
        self.rule_engine = ItineraryEngine()
        self.ai_engine = DeepSeekItineraryGenerator()

    def generate(self, request):

        if self.mode == "rule":
            return self.rule_engine.generate(request)

        ai_result = None

        if self.mode in ("auto", "ai"):
            ai_result = self.ai_engine.generate(request)

        if ai_result is None:
            logger.info(
                "Using rule-based itinerary engine (mode=%s)", self.mode
            )
            return self.rule_engine.generate(request)

        return ai_result


if __name__ == "__main__":

    import sys
    from pathlib import Path

    ROOT = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(ROOT))

    from models.travel_request import TravelRequest

    req = TravelRequest()

    req.raw_text = (
        "4 days Kathmandu Pokhara for 2 adults, 4 star, "
        "prefer hiking and culture"
    )
    req.destinations = ["Kathmandu", "Pokhara"]
    req.days = 4
    req.adults = 2
    req.pax = 2

    gen = SmartItineraryGenerator()

    for day in gen.generate(req):
        print(day)
