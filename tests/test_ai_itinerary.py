import os
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).parent.parent)
)

from models.travel_request import TravelRequest
from itinerary.ai_itinerary_generator import (
    DeepSeekItineraryGenerator,
    OpenAIItineraryGenerator,
    SmartItineraryGenerator,
)

saved_key = os.environ.get("DEEPSEEK_API_KEY", "")
saved_openai = os.environ.get("OPENAI_API_KEY", "")
saved_provider = os.environ.get("AI_PROVIDER", "")
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

print("=== Test 4: provider selection ===")

os.environ["OPENAI_API_KEY"] = "sk-test-openai"
os.environ["AI_PROVIDER"] = "openai"
os.environ["DEEPSEEK_API_KEY"] = ""

gen_openai = SmartItineraryGenerator(mode="auto")

assert isinstance(
    gen_openai._select_ai_engine(), OpenAIItineraryGenerator
), "AI_PROVIDER=openai must select OpenAI engine"
assert gen_openai.openai_engine.api_key == "sk-test-openai"
assert gen_openai.openai_engine.model == "gpt-4o-mini"
assert gen_openai.openai_engine.base_url == "https://api.openai.com/v1"

os.environ["AI_PROVIDER"] = "deepseek"

gen_ds = SmartItineraryGenerator(mode="auto")

assert isinstance(
    gen_ds._select_ai_engine(), DeepSeekItineraryGenerator
), "AI_PROVIDER=deepseek must select DeepSeek engine"

os.environ["AI_PROVIDER"] = "auto"
os.environ["DEEPSEEK_API_KEY"] = "sk-test-ds"
os.environ["OPENAI_API_KEY"] = ""

gen_auto_ds = SmartItineraryGenerator(mode="auto")

assert isinstance(
    gen_auto_ds._select_ai_engine(), DeepSeekItineraryGenerator
), "auto must prefer DeepSeek key"

os.environ["DEEPSEEK_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = "sk-test-openai"

gen_auto_oa = SmartItineraryGenerator(mode="auto")

assert isinstance(
    gen_auto_oa._select_ai_engine(), OpenAIItineraryGenerator
), "auto with only OpenAI key must select OpenAI"

os.environ["OPENAI_API_KEY"] = ""
os.environ["AI_PROVIDER"] = "auto"

gen_none = SmartItineraryGenerator(mode="auto")

assert gen_none._select_ai_engine() is None, "no keys -> no AI engine"

print("OK: provider selection passed")

print("=== Test 5: rule mode unaffected by provider ===")

os.environ["OPENAI_API_KEY"] = "sk-test-openai"

gen_rule = SmartItineraryGenerator(mode="rule")

result_rule2 = gen_rule.generate(request)

assert result_rule2 == result, "rule mode must stay identical"

print("OK: rule mode still identical")

print("=== Test 6: duration prompt guidance ===")

gen_prompt = SmartItineraryGenerator(mode="rule")

req_no_dur = TravelRequest()
req_no_dur.raw_text = "Nepal trip to Kathmandu Pokhara Chitwan for 2 people"
req_no_dur.destinations = ["Kathmandu", "Pokhara", "Chitwan"]
req_no_dur.pax = 2
req_no_dur.days = 0
req_no_dur.nights = 0

prompt_auto = gen_prompt.deepseek_engine._build_prompt(req_no_dur)

assert "did not specify a trip duration" in prompt_auto, (
    "no-duration prompt must tell the AI to infer a duration"
)
assert "1 to 2 days per major destination" in prompt_auto

req_with_days = TravelRequest()
req_with_days.raw_text = "10 days Nepal tour"
req_with_days.destinations = ["Kathmandu", "Pokhara", "Chitwan", "Lumbini"]
req_with_days.days = 10

prompt_days = gen_prompt.deepseek_engine._build_prompt(req_with_days)

assert "build exactly 10 day(s)" in prompt_days

req_with_nights = TravelRequest()
req_with_nights.raw_text = "5 nights Pokhara"
req_with_nights.destinations = ["Pokhara"]
req_with_nights.nights = 5

prompt_nights = gen_prompt.deepseek_engine._build_prompt(req_with_nights)

assert "5-night trip" in prompt_nights

print("OK: duration prompt guidance passed")

os.environ["DEEPSEEK_API_KEY"] = saved_key
os.environ["OPENAI_API_KEY"] = saved_openai
os.environ["AI_PROVIDER"] = saved_provider

print("ALL TESTS PASSED")
