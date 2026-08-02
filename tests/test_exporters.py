from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

sys.path.append(
    str(ROOT)
)

from exports.pdf_exporter import PDFExporter
from exports.docx_exporter import DOCXExporter

exports_dir = ROOT / "data" / "exports"
exports_dir.mkdir(parents=True, exist_ok=True)

pdf = PDFExporter()

docx = DOCXExporter()

print(
    pdf.export(
        str(exports_dir / "sample.pdf"),
        "PM Automation PDF Test"
    )
)

print(
    docx.export(
        str(exports_dir / "sample.docx"),
        "PM Automation DOCX Test"
    )
)
