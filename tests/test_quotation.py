from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

sys.path.append(
    str(ROOT)
)

from exports.pdf_exporter import PDFExporter
from exports.docx_exporter import DOCXExporter
from orchestrators.manual_request_orchestrator import ManualRequestOrchestrator

engine = ManualRequestOrchestrator()

text = """
My name is John Smith

Email john@test.com

Phone +9779811111111

We are 6 pax

Kathmandu Pokhara Chitwan

Budget 2500 USD
"""

result = engine.process(text)

itinerary_text = str(result["itinerary"])
costing_text = str(result["costing"])

full_text = f"""

PM AUTOMATION QUOTATION

======================

ITINERARY

{itinerary_text}

======================

COSTING

{costing_text}

"""

quotations_dir = ROOT / "data" / "quotations"
quotations_dir.mkdir(parents=True, exist_ok=True)

PDFExporter().export(
    str(quotations_dir / "quotation.pdf"),
    full_text
)

DOCXExporter().export(
    str(quotations_dir / "quotation.docx"),
    full_text
)

print("PDF CREATED")
print("DOCX CREATED")
