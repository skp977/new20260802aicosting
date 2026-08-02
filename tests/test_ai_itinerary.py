import os
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).parent.parent)
)

from models.travel_request import TravelRequest
from itinerary.ai_itinerary_generator import (
    DeepSeekItineraryGenerator,
    SmartItineraryGenerator,
)

saved_key = os.environ.get("DEEPSEEK_API_KEY", "")
os.environ["DEEPSEEK_API_KEY"] = ""

request = TravelRequest()

request.raw_text = (
    "4 days Kathmandu Pokhara for 2 adults, 4 star, "
    "prefer hiking and culture"
)
request.destinations = ["Kathmandu", "Pokhara"]
request.days = 4
request.nights = 3
request.adults = 2
request.pax = 2
request.hotel_category = "4 Star"

print("=== Test 1: fallback to rule engine when no API key ===")

gen = SmartItineraryGenerator(mode="auto")

result = gen.generate(request)

assert isinstance(result, list) and result, "expected non-empty itinerary"
assert all("day" in day for day in result), "every day needs a day number"
assert all("activities" in day for day in result), "every day needs activities"
assert len(result) == len(request.destinations), "rule fallback = 1 day per destination"

print(f"OK: {len(result)} days from rule fallback")
for day in result:
    print(
        f"  Day {day['day']}: {day['title']} "
        f"[{day['hotel_category']}] {len(day['activities'])} activities"
    )

print("=== Test 2: rule mode forces rule engine ===")

gen_rule = SmartItineraryGenerator(mode="rule")

result_rule = gen_rule.generate(request)

assert result_rule == result, "rule mode should equal auto-without-key"

print("OK: rule mode identical")

print("=== Test 3: JSON normalization of AI output ===")

raw_ai_json = """
```json
{"itinerary": [
  {"day": 7, "title": "Explore Kathmandu Valley",
   "city": "kathmandu", "overnight": "Kathmandu",
   "hotel_category": "4-star", "meals": ["Breakfast"],
   "transport": "Private Vehicle",
   "activities": "Pashupatinath, Boudhanath",
   "notes": "Half-day drive from Pokhara."},
  {"city": "Pokhara", "hotel_category": "5 Star",
   "meals": ["Breakfast", "Lunch", "Dinner"],
   "activities": ["Phewa Lake", "Sarangkot", "World Peace Pagoda"],
   "transport": "Domestic Flight (KTM-PKR)",
   "notes": "Morning flight, altitude 827m."}
]}
```
"""

parser = DeepSeekItineraryGenerator(
    api_key="", model="deepseek-chat"
)

days = parser._parse_itinerary(raw_ai_json, request)

assert days[0]["day"] == 1, "day numbers must be sequential from 1"
assert days[0]["city"] == "kathmandu", "city should be preserved as given"
assert days[0]["hotel_category"] == "4 Star", "4-star must normalize"
assert days[0]["meals"] == ["Breakfast", "Dinner"], "Dinner must be appended"
assert days[0]["activities"] == ["Pashupatinath, Boudhanath"]
assert days[1]["hotel_category"] == "5 Star"
assert days[1]["overnight"] == "Pokhara"
assert len(days) == 2

print("OK: normalization passed")
print("  Day 1:", days[0])
print("  Day 2:", days[1])

os.environ["DEEPSEEK_API_KEY"] = saved_key

print("ALL TESTS PASSED")
