import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)


from parsers.travel_request_extractor import *

text="""
Hello

My name is John.

We are 6 pax.

Want Kathmandu Pokhara Chitwan.

Budget 2500 USD.

Email john@test.com

Phone +9779811111111
"""

x=TravelRequestExtractor()

r=x.extract(text)

print(r)
