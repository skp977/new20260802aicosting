"""
FILE NAME:
ai_itinerary_generator.py

PURPOSE:
Generate travel itineraries from a natural-language prompt using an
LLM provider (DeepSeek or OpenAI, both OpenAI-compatible). Falls back
to the rule-based ItineraryEngine when no API key is configured or the
AI call fails. Provider chosen via AI_PROVIDER (deepseek|openai|auto).

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
from websearch.search_engine import WebSearchEngine

logger = logging.getLogger(__name__)

HOTEL_CATEGORIES = ["3 Star", "4 Star", "5 Star"]

SYSTEM_PROMPT = (
    "You are a senior Nepal travel itinerary planner with expert local "
    "knowledge. You build realistic, day-by-day itineraries tailored to the "
    "traveler's request.\n\n"
    "Respond with ONLY valid JSON. No markdown, no code fences, no prose.\n"
    'The JSON must be exactly: {"itinerary": [day, day, ...], '
    '"price_estimate": {...} or null} where each day '
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
    '"price_estimate": null when no reliable price is available; otherwise '
    'use the shape {"per_person": <number>, "currency": "<3-letter code>", '
    '"note": "<1-2 sentences citing the live web sources, e.g. Based on '
    "latest tour operator listings, ~$120-150/person/day inclusive.\"}. "
    "Base the price on the LIVE WEB DATA provided in the user message, not "
    "on your own guesses.\n\n"
    "Constraints:\n"
    "- Produce the exact number of days requested.\n"
    "- Use real, verifiable places and standard Nepal tourism routes.\n"
    "- Vary the itinerary intelligently; do not repeat the same template."
)


class DeepSeekItineraryGenerator:

    def __init__(self, api_key=None, model=None, base_url=None, timeout=None):

        self.name = "DeepSeek"
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.base_url = base_url or os.getenv(
            "DEEPSEEK_BASE_URL", "https://api.deepseek.com"
        )
        self.timeout = int(
            timeout or os.getenv("DEEPSEEK_TIMEOUT", "60")
        )

        self.web_search = WebSearchEngine()
        self.last_price_estimate = None

    def generate(self, request):

        if not self.api_key:
            logger.info(
                "%s API key not set; AI itinerary skipped", self.name
            )
            return None

        self.last_price_estimate = None

        web_data = self._search_web(request)

        prompt = self._build_prompt(request, web_data)

        try:
            content = self._call_api(prompt)
        except Exception as exc:
            logger.warning(
                "%s itinerary call failed: %s", self.name, exc
            )
            return None

        return self._parse_itinerary(content, request)

    def _build_prompt(self, request, web_data=None):

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
        elif request.nights > 0:
            lines.append(
                f"\nIMPORTANT: build a {request.nights}-night trip "
                f"(i.e. {request.nights} nights of overnight stays, "
                f"usually {request.nights + 1} calendar days)."
            )
        else:
            lines.append(
                "\nThe customer did not specify a trip duration. "
                "Choose a realistic duration yourself and build exactly "
                "that many days, based on the destinations and activities: "
                "as a rule of thumb allow 1 to 2 days per major destination "
                "(minimum 1 day, maximum 14 days). State the chosen total "
                "number of days in the title of day 1."
            )

        if web_data:
            lines.append(self._format_web_data(web_data))

        return "\n\n".join(lines) or "Build a 3-day Nepal itinerary."

    def _search_web(self, request):

        destinations = request.destinations or ["Kathmandu"]

        place = ", ".join(destinations[:3])

        days_text = f" {request.days} day" if request.days > 0 else ""

        queries = []

        if request.days > 0:
            queries.append(
                f"{place} Nepal tour package itinerary {request.days} days"
            )
        else:
            queries.append(
                f"{place} Nepal tour package itinerary"
            )

        queries.append(
            f"{place} Nepal tour package price per person{days_text}"
        )

        results = []

        for query in queries:
            results.extend(
                self.web_search.search(query)
            )

        return results

    def _format_web_data(self, web_data):

        lines = [
            "\nLIVE WEB DATA (from the internet, use this for realistic "
            "routes, activities, and current market prices):"
        ]

        for item in web_data[:12]:
            title = item.get("title", "")
            url = item.get("url", "")
            snippet = item.get("snippet", "")

            lines.append(f"- {title} ({url})")
            if snippet:
                lines.append(f"  {snippet}")

        return "\n".join(lines)

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
            self.last_price_estimate = self._extract_price_estimate(data)
        else:
            days = data
            self.last_price_estimate = None

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

    def _extract_price_estimate(self, data):

        estimate = (
            data.get("price_estimate")
            or data.get("estimated_price")
            or data.get("price")
        )

        if not estimate:
            return None

        if isinstance(estimate, (int, float)):
            return {
                "per_person": float(estimate),
                "currency": "USD",
                "note": "",
            }

        if not isinstance(estimate, dict):
            return None

        per_person = estimate.get("per_person")
        currency = str(estimate.get("currency") or "USD").upper()
        note = str(estimate.get("note") or "").strip()

        if per_person is None:
            low = estimate.get("low")
            high = estimate.get("high")
            if isinstance(low, (int, float)) and isinstance(high, (int, float)):
                return {
                    "per_person": round(
                        (float(low) + float(high)) / 2, 2
                    ),
                    "currency": currency,
                    "note": f"Range {low}-{high} {currency}. {note}".strip(),
                }
            return None

        return {
            "per_person": float(per_person),
            "currency": currency,
            "note": note,
        }

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


class OpenAIItineraryGenerator(DeepSeekItineraryGenerator):

    def __init__(self, api_key=None, model=None, base_url=None, timeout=None):

        self.name = "OpenAI"
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.base_url = base_url or os.getenv(
            "OPENAI_BASE_URL", "https://api.openai.com/v1"
        )
        self.timeout = int(
            timeout or os.getenv("OPENAI_TIMEOUT", "60")
        )


class SmartItineraryGenerator:

    def __init__(self, mode=None, provider=None):

        self.mode = (mode or os.getenv("ITINERARY_ENGINE", "auto")).lower()
        self.provider = (
            provider or os.getenv("AI_PROVIDER", "auto")
        ).lower()

        self.rule_engine = ItineraryEngine()
        self.deepseek_engine = DeepSeekItineraryGenerator()
        self.openai_engine = OpenAIItineraryGenerator()

        self.last_price_estimate = None

    def _select_ai_engine(self):

        if self.provider == "deepseek":
            return self.deepseek_engine
        if self.provider == "openai":
            return self.openai_engine

        if self.deepseek_engine.api_key:
            return self.deepseek_engine
        if self.openai_engine.api_key:
            return self.openai_engine

        return None

    def generate(self, request):

        self.last_price_estimate = None

        if self.mode == "rule":
            return self.rule_engine.generate(request)

        ai_result = None

        if self.mode in ("auto", "ai"):
            ai_engine = self._select_ai_engine()

            if ai_engine is not None:
                ai_result = ai_engine.generate(request)
                self.last_price_estimate = (
                    ai_engine.last_price_estimate
                )

        if ai_result is None:
            logger.info(
                "Using rule-based itinerary engine "
                "(mode=%s, provider=%s)",
                self.mode,
                self.provider,
            )
            self.last_price_estimate = None
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
