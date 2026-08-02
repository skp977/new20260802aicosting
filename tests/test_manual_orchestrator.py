from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).parent.parent)
)

from orchestrators.manual_request_orchestrator import ManualRequestOrchestrator

text = """
My name is John Smith

Email john@test.com

Phone +9779811111111

We are 6 pax

Kathmandu Pokhara Chitwan

Budget 2500 USD
"""

engine = ManualRequestOrchestrator()

result = engine.process(text)

print("=" * 60)
print(result["request"])
print("=" * 60)
print(result["itinerary"])
print("=" * 60)
print(result["costing"])
print("=" * 60)
