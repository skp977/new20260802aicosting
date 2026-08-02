import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from parsers.universal_parser import UniversalParser

parser = UniversalParser()

print(parser.parse("Hello Nepal"))
print(parser.parse("https://example.com"))
print(parser.parse("test.pdf"))
